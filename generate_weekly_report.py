
import pandas as pd
import numpy as np

# ---------- SETTINGS (change these if needed) ----------
DATA_FOLDER = "."                  # "." means: the folder this script is in
REPORT_DATE = None                 # None = use the latest ticket date.
OUTPUT_FILE = "weekly_report.xlsx"


# ---------- STEP 1: LOAD THE DATA ----------
incidents = pd.read_csv(DATA_FOLDER + "/incidents.csv", parse_dates=["raised_date", "resolved_date"])
changes = pd.read_csv(DATA_FOLDER + "/changes.csv", parse_dates=["request_date", "approval_date", "implementation_date"])
surveys = pd.read_csv(DATA_FOLDER + "/surveys.csv", parse_dates=["survey_sent_date", "response_date"])

print("Loaded:", len(incidents), "incidents,", len(changes), "changes,", len(surveys), "surveys")


# ---------- STEP 2: CHECK THE DATA ----------
results = []

def add_check(check, table, issues):
    results.append({
        "check": check,
        "table": table,
        "issues_found": int(issues),
        "status": "PASS" if issues == 0 else "FAIL",
    })

add_check("Null values", "incidents", incidents.isna().sum().sum())
add_check("Null values", "changes", changes.isna().sum().sum())
add_check("Null values", "surveys", surveys.isna().sum().sum())
add_check("Duplicate ticket_id", "incidents", incidents["ticket_id"].duplicated().sum())
add_check("Duplicate change_id", "changes", changes["change_id"].duplicated().sum())
add_check("Duplicate survey_id", "surveys", surveys["survey_id"].duplicated().sum())
add_check("More than one survey per ticket", "surveys", surveys["ticket_id"].duplicated().sum())
add_check("Survey with no matching ticket", "surveys", (~surveys["ticket_id"].isin(incidents["ticket_id"])).sum())
add_check("Resolved before raised", "incidents", (incidents["resolved_date"] < incidents["raised_date"]).sum())
add_check("Response before survey sent", "surveys", (surveys["response_date"] < surveys["survey_sent_date"]).sum())
add_check("CSAT outside 1-5", "surveys", (~surveys["csat_score"].between(1, 5)).sum())

calc_hours = (incidents["resolved_date"] - incidents["raised_date"]).dt.total_seconds() / 3600
calc_status = np.where(calc_hours <= incidents["sla_target_hours"], "Met", "Breached")
add_check("SLA status mismatch", "incidents", (calc_status != incidents["sla_status"]).sum())

validation = pd.DataFrame(results)
failed = validation[validation["status"] == "FAIL"]

if len(failed) == 0:
    print("Validation: all", len(validation), "checks passed")
else:
    print("WARNING:", len(failed), "check(s) failed:")
    print(failed.to_string(index=False))


# ---------- STEP 3: PICK THE REPORTING WEEK ----------
if REPORT_DATE is None:
    report_end = incidents["raised_date"].max().normalize()
else:
    report_end = pd.Timestamp(REPORT_DATE).normalize()

week_start = report_end - pd.Timedelta(days=6)        # 7 days ending on report_end
prev_start = week_start - pd.Timedelta(days=7)        # the 7 days before that
day_after = report_end + pd.Timedelta(days=1)

print("Reporting week:", week_start.date(), "to", report_end.date())


# ---------- STEP 4: WEEKLY NUMBERS (this week vs previous week) ----------
def window_kpis(inc, sur, start, end_exclusive):
    w = inc[(inc["raised_date"] >= start) & (inc["raised_date"] < end_exclusive)]
    w_sur = sur[sur["ticket_id"].isin(w["ticket_id"])]
    breached = w[w["sla_status"] == "Breached"]
    top_cat = breached["category"].value_counts().idxmax() if len(breached) else "None"
    hours = (w["resolved_date"] - w["raised_date"]).dt.total_seconds() / 3600

    return {
        "Tickets raised": len(w),
        "SLA compliance %": round((w["sla_status"] == "Met").mean() * 100, 1),
        "Breached tickets": len(breached),
        "Avg resolution hours": round(hours.mean(), 1),
        "Avg CSAT (1-5)": round(w_sur["csat_score"].mean(), 2),
        "Survey response rate %": round(len(w_sur) / len(w) * 100, 1),
        "Top breach category": top_cat,
    }

this_week = window_kpis(incidents, surveys, week_start, day_after)
prev_week = window_kpis(incidents, surveys, prev_start, week_start)

summary = pd.DataFrame({"this week": this_week, "previous week": prev_week})

nums = summary.drop("Top breach category").astype(float)
nums["change"] = (nums["this week"] - nums["previous week"]).round(2)
top_category_row = summary.loc[["Top breach category"]]


# ---------- STEP 5: SLA COMPLIANCE TABLES (all data) ----------
incidents["is_met"] = incidents["sla_status"] == "Met"
incidents["month"] = incidents["raised_date"].dt.strftime("%Y-%m")

by_priority = (incidents.groupby("priority")["is_met"].mean() * 100).round(1).rename("compliance_pct")
by_team = (incidents.groupby("team")["is_met"].mean() * 100).round(1).rename("compliance_pct")
by_category = (incidents.groupby("category")["is_met"].mean() * 100).round(1).rename("compliance_pct")
by_month = (incidents.groupby("month")["is_met"].mean() * 100).round(1).rename("compliance_pct")


# ---------- STEP 6: CSAT ----------
csat = surveys.merge(incidents[["ticket_id", "sla_status"]], on="ticket_id", how="left")
csat_by_sla = csat.groupby("sla_status")["csat_score"].agg(responses="count", avg_csat="mean").round(2)


# ---------- STEP 7: CHANGE MANAGEMENT ----------
changes["failed"] = changes["outcome"] != "Successful"

fail_by_risk = changes.groupby("risk_level").agg(total_changes=("change_id", "count"), failed=("failed", "sum"))
fail_by_risk["failure_rate_pct"] = (fail_by_risk["failed"] / fail_by_risk["total_changes"] * 100).round(1)
fail_by_risk = fail_by_risk.reindex(["Low", "Medium", "High"])

approval = changes.groupby("change_type")["approval_turnaround_hours"].mean().round(1).rename("avg_approval_hours")


# ---------- STEP 8: SAVE EVERYTHING TO EXCEL ----------
with pd.ExcelWriter(OUTPUT_FILE) as writer:
    nums.to_excel(writer, sheet_name="Weekly Summary")
    top_category_row.to_excel(writer, sheet_name="Weekly Summary", startrow=len(nums) + 3)
    by_priority.to_excel(writer, sheet_name="SLA by Priority")
    by_team.to_excel(writer, sheet_name="SLA by Team")
    by_category.to_excel(writer, sheet_name="SLA by Category")
    by_month.to_excel(writer, sheet_name="SLA by Month")
    csat_by_sla.to_excel(writer, sheet_name="CSAT by SLA")
    fail_by_risk.to_excel(writer, sheet_name="Change Risk")
    approval.to_excel(writer, sheet_name="Approval Time")
    validation.to_excel(writer, sheet_name="Validation", index=False)

print("Report saved to", OUTPUT_FILE)
