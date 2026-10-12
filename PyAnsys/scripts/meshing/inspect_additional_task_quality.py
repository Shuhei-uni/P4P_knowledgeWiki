"""Read the guided-workflow table of additional quality methods."""
from build_single_inlet_family import *
s=connect();s.events.stop()
task=s.workflow.TaskObject['Improve Volume Mesh'];old=plain(task.Arguments.get_state())
try:
    task.Arguments.update_dict({'AddMultipleQualityMethods':'Yes'})
    info={'arguments':plain(task.Arguments.get_state())}
    save_json(OUT/'additional-task-quality.json',info);print(json.dumps(info,indent=2),flush=True)
finally:task.Arguments.set_state(old)
