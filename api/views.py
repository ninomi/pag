from django.http import JsonResponse
from django.views.decorators.http import require_GET
from pag import utils
from datetime import datetime

@require_GET
def projects(request):
    try:
        backlog = utils.backlog(request, request.session['space'], token=request.session['token'])
        projects = backlog.get_projects().json()
    except KeyError:
        projects = []
    return JsonResponse(projects, safe=False)


@require_GET
def grade(request, project_id):
    try:
        backlog = utils.backlog(request, request.session['space'], token=request.session['token'])

        # get project issue
        issues = backlog.get_issues(project_id).json()

        # grade data initialize
        detailed_issue_count = 0
        all_issue_count = backlog.get_count_issues(project_id).json()["count"]

        detailed_comment_count = 0
        all_comment_count = 0

        closed_issue_count = 0
        closed_issue_with_comment_count = 0
        closed_issue_with_atime_count = 0
        closed_issue_with_resolution_count = 0

        readied_issue_count = 0
        readied_issue_with_ddate_count = 0
        readied_issue_with_assigner_count = 0
        readied_issue_with_etime_count = 0
        readied_issue_with_milestones_count = 0

        expired_issue_count = 0
        expired_closed_issue_count = 0

        # advice data initialize
        adv_issues_little_detailed = []
        adv_issues_little_comment = []
        adv_closed_issues_no_comment = []
        adv_readied_issue_no_duedate = []
        adv_readied_issues_no_estimated = []
        adv_expired_closed_issues = []
        adv_closed_issues_no_actualHours = []
        adv_readied_issues_no_assigner = []
        adv_closed_issues_no_resolution = []
        adv_readied_issues_no_milestones = []

        for issue in issues:
            # get comment
            comments = backlog.get_comment(issue["id"]).json()
            for comment in comments:
                point = utils.get_linear_point(len(comment["content"])) if comment["content"] else 0
                detailed_comment_count += point
                adv_issues_little_comment = utils.append_adv_issues(adv_issues_little_comment, issue["issueKey"]+"#comment-"+str(comment["id"]), point)
                all_comment_count += 1

            point = utils.get_linear_point(len(issue["description"]))
            detailed_issue_count += point
            adv_issues_little_detailed = utils.append_adv_issues(adv_issues_little_detailed, issue["issueKey"], point)

            if issue["status"]["id"] == 4:
                closed_issue_count += 1
                if len(comments) >= 1: 
                    closed_issue_with_comment_count += 1
                else:
                    adv_closed_issues_no_comment.append(issue["issueKey"])
                if issue["actualHours"] is None: 
                    closed_issue_with_atime_count += 1
                else:
                    adv_closed_issues_no_actualHours.append(issue["issueKey"])
                if not issue["resolution"] is None: 
                    closed_issue_with_resolution_count += 1
                else:
                    adv_closed_issues_no_resolution.append(issue["issueKey"])

            if not issue["startDate"] is None:
                readied_issue_count += 1
                if not issue["dueDate"] is None: 
                    readied_issue_with_ddate_count += 1 
                else:
                    adv_readied_issue_no_duedate.append(issue["issueKey"])
                if not issue["assignee"] is None: 
                    readied_issue_with_assigner_count += 1
                else:
                    adv_readied_issues_no_assigner.append(issue["issueKey"])
                if not issue["estimatedHours"] is None: 
                    readied_issue_with_etime_count += 1
                else:
                    adv_readied_issues_no_estimated.append(issue["issueKey"])

                if not len(issue["milestone"]) == 0 : 
                    readied_issue_with_milestones_count += 1
                else:
                    adv_readied_issues_no_milestones.append(issue["issueKey"])

            if not issue["dueDate"] is None and datetime.strptime(issue["dueDate"], '%Y-%m-%dT%H:%M:%SZ') < datetime.today(): 
              expired_issue_count += 1
              if issue["status"]["id"] == 4: 
                  expired_closed_issue_count += 1 
              else:
                  adv_expired_closed_issues.append(issue["issueKey"])

        # out put data

        adv_issues_little_comment = list(set(adv_issues_little_comment))
        advice_rows = [
                ["もっと詳細を詳細に書こう",                 adv_issues_little_detailed],
                ["もう少し詳しくコメントを書いてあげよう",   adv_issues_little_comment],
                ["終了したチケットにコメントを残そう",       adv_closed_issues_no_comment],
                ["期限日を入力しよう",                       adv_readied_issue_no_duedate],
                ["実績時間を入力しよう",                     adv_readied_issues_no_estimated],
                ["期限を過ぎているタスクを終了しよう",       adv_expired_closed_issues],
                ["実績時間を入力しよう",                     adv_closed_issues_no_actualHours],
                ["チケットへ担当者をアサインしよう",         adv_readied_issues_no_assigner],
                ["終了したチケットに完了理由をを入力しよう", adv_closed_issues_no_resolution],
                ["チケットをマイルストーンへ関連づけよう",   adv_readied_issues_no_milestones],
                ["",   []]
                ]

        advice_key = ["message","issues"]
        result_advice = utils.set_Dict(advice_key,advice_rows)

        point_detailed_issue = utils.get_point(detailed_issue_count, all_issue_count, 10)
        point_detailed_comment = utils.get_point(detailed_comment_count, all_comment_count, 10)
        point_closed_issue_with_comment = utils.get_point(closed_issue_with_comment_count, closed_issue_count, 10)
        point_readied_issue_with_date = utils.get_point(readied_issue_with_ddate_count, readied_issue_count, 10)
        point_readies_issue_with_estimated_hours = utils.get_point(readied_issue_with_etime_count, readied_issue_count, 10)
        point_expired_and_closed_issue = utils.get_point(expired_closed_issue_count, expired_issue_count, 10)
        point_closed_issue_with_actual_hours = utils.get_point(closed_issue_with_atime_count, closed_issue_count, 10)
        point_readies_issue_with_assigner = utils.get_point(readied_issue_with_assigner_count, readied_issue_count, 10)
        point_closed_issue_with_resolution = utils.get_point(closed_issue_with_resolution_count, closed_issue_count, 10)
        point_readied_issue_with_milestones = utils.get_point(readied_issue_with_milestones_count, readied_issue_count, 10)

        total_point = point_detailed_issue + point_detailed_comment + point_closed_issue_with_comment + point_readied_issue_with_date + point_readies_issue_with_estimated_hours + point_expired_and_closed_issue + point_closed_issue_with_actual_hours + point_readies_issue_with_assigner + point_closed_issue_with_resolution + point_readied_issue_with_milestones

        grade_rows = [
                utils.get_row("Total Point",                     0,                 0,     total_point, result_advice[10]),
                utils.get_row("Detailed issue",                     detailed_issue_count,                 all_issue_count,     point_detailed_issue, result_advice[0]),
                utils.get_row("Detailed comment",                   detailed_comment_count,               all_comment_count,   point_detailed_comment, result_advice[1]),
                utils.get_row("Closed issue with comment",          closed_issue_with_comment_count,      closed_issue_count,  point_closed_issue_with_comment, result_advice[2]),
                utils.get_row("Readied issue with due date",        readied_issue_with_ddate_count,       readied_issue_count, point_readied_issue_with_date, result_advice[3]),
                utils.get_row("Readied issue with estimated hours", readied_issue_with_etime_count,       readied_issue_count, point_readies_issue_with_estimated_hours, result_advice[4]),
                utils.get_row("Expired and closed issue",           expired_closed_issue_count,           expired_issue_count, point_expired_and_closed_issue, result_advice[5]),
                utils.get_row("Closed issue with actual hours",     closed_issue_with_atime_count,        closed_issue_count,  point_closed_issue_with_actual_hours, result_advice[6]),
                utils.get_row("Readied issue with assigner",        readied_issue_with_assigner_count,    readied_issue_count, point_readies_issue_with_assigner, result_advice[7]),
                utils.get_row("Closed issue with resolution",       closed_issue_with_resolution_count,   closed_issue_count,  point_closed_issue_with_resolution, result_advice[8]),
                utils.get_row("Readied issue with milestones",      readied_issue_with_milestones_count,  readied_issue_count, point_readied_issue_with_milestones, result_advice[9])
                ]
        grade_key = ["title","count","all_count","point", "advice"]
        result_grade = utils.set_Dict(grade_key, grade_rows)

    except KeyError:
        result_grade = []
    return JsonResponse(result_grade, safe=False)

