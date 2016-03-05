import pandas as pd
import numpy as np
from sklearn import linear_model

#parametrs
time_lag = 12*60*60
course_start_date = 1423972800
w2_start_date = course_start_date + 7*24*60*60
w3_start_date = course_start_date + 14*24*60*60
course_end_date = course_start_date + 35*24*60*60

module_start = {1 : course_start_date, 2 : w2_start_date, 3 :course_end_date}

#course structure
course_structure = pd.read_table("course-76-structure.csv", sep =",")

#steps history
history_steps = pd.read_table("course-76-history-steps.csv", sep = ",")
history_steps = history_steps.loc[history_steps["history_user"] != 0]
history_steps = history_steps.loc[history_steps["history_date"] > course_start_date]

step_edits_number = history_steps.groupby("step_id").size().reset_index()
step_edits_number.columns = ['step_id', 'total_edits']

# comments
comments = pd.read_table("course-76-comments.csv", sep=",")
comments = comments.loc[comments["time"] > course_start_date]

#get change time
history_data = pd.DataFrame()
for i in course_structure.step_id:
    step_id = i
    step_module = course_structure.loc[course_structure["step_id"] == step_id].module_position
    step_type = course_structure.loc[course_structure["step_id"] == step_id].step_type
    start_time = module_start[int(step_module)]

    step_history = history_steps.loc[(history_steps["step_id"] == step_id) &
                                     (history_steps["history_date"] > start_time) &
                                     ((history_steps["history_date"] < course_end_date))]
    if len(step_history) < 1:
        step_data = pd.DataFrame({"step_id": step_id, "step_type": step_type, "start": start_time, "end": course_end_date, "is_changed":  0,
                 "prev_changes": 0 })
        history_data = pd.concat((history_data, step_data))
        continue
    step_history_stat = step_history.groupby("history_date").size().reset_index().values

    changes_date = np.insert(step_history_stat[:, 0], [0, len(step_history_stat[:, 0])], [course_start_date, course_end_date])
    change_point_index = np.where(np.diff(changes_date) > time_lag)[0]

    start = changes_date[change_point_index]
    end = changes_date[np.add(change_point_index,1)]
    is_changed = np.where(end == course_end_date, 0, 1)
    step_type = np.tile(step_type, len(change_point_index))
    #change_lenght =
    change_number = np.arange(len(change_point_index))
    id = np.tile(step_id, len(change_point_index))

    step_data = pd.DataFrame({"step_id": id, "step_type": step_type, "start": start, "end": end, "is_changed":  is_changed,
                 "prev_changes": change_number })


    history_data = pd.concat((history_data, step_data))



# check all step
len(course_structure.step_id) == len(np.unique(history_data.step_id))