"""Read the version-matched mesh-improvement controls and allowed methods."""
from build_single_inlet_family import *
s=connect();s.events.stop()
args=s.meshing.ImproveVolumeMesh.create_instance()
data={'state':plain(args.get_state()),'quality_methods':plain(args.QualityMethod.allowed_values()),
      'multiple_methods':plain(args.QualityMethodList.allowed_values()),
      'add_multiple':plain(args.AddMultipleQualityMethods.allowed_values())}
save_json(OUT/'quality-control-capabilities.json',data);print(json.dumps(data,indent=2),flush=True)
args.AddMultipleQualityMethods.set_state('Yes')
data2={'state':plain(args.get_state()),'multiple_methods':plain(args.QualityMethodList.allowed_values()),
       'criteria_attrs':plain(args.QualityCriteriaList.get_attr('default'))}
save_json(OUT/'additional-quality-capabilities.json',data2);print(json.dumps(data2,indent=2),flush=True)
