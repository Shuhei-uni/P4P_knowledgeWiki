# Documentation Map for Agent Fallback

Use this when the live Fluent/PyFluent path does not match the local notes.

## Primary references

| Topic | Use when | URL |
|---|---|---|
| PyFluent documentation | Need current PyFluent API patterns, examples, generated settings objects | https://fluent.docs.pyansys.com/ |
| PyFluent Settings APIs and objects blog | Need examples for inspecting settings objects, child names, commands, object structure | https://developer.ansys.com/blog/all-you-need-know-about-pyfluents-settings-apis-and-objects |
| PyFluent GitHub | Need package source, issues, examples, version compatibility notes | https://github.com/ansys/pyfluent |
| Fluent DPM User Guide section | Need DPM/injection workflow and theory of injection inputs | https://ansyshelp.ansys.com/public/Views/Secured/corp/v251/en/flu_ug/flu_ug_sec_discrete_use_oview.html |
| Fluent multiphase theory: approaches | Need VOF/Mixture/Eulerian distinctions | https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_th/flu_th_sec_mphase_approaches.html |
| Fluent Eulerian Wall Film options | Need EWF activation/options | https://ansyshelp.ansys.com/public/Views/Secured/corp/v242/en/flu_ug/flu_ug_ewf_sec_options.html |
| Fluent Text Command List / TUI | Need TUI fallback or prompts when PyFluent settings API fails | https://ansyshelp.ansys.com/public/Views/Secured/corp/v242/en/flu_tcl/flu_tcl_appx_tuichanges.html |
| Fluent 2024 R2 TUI changes | Need version-specific command changes | https://ansyshelp.ansys.com/public/Views/Secured/corp/v242/en/flu_mig/flu_mig_chp_tui.html |

## Search recipes

When a path fails, search the web or Ansys Help with queries like:

```text
site:ansyshelp.ansys.com Fluent 2024 R2 <model name> <setting name>
site:fluent.docs.pyansys.com <setting object or command name>
PyFluent settings API child_names command_names <model name>
Ansys Fluent TUI <menu path> <setting name>
```

For DPM injection failures:

```text
PyFluent discrete phase injection surface location Fluent
Ansys Fluent TUI define models dpm injections surface
Fluent DPM injection material inert_particle PyFluent
```

For multiphase failures:

```text
Fluent Mixture model surface tension 2024 R2
Fluent VOF phase interaction surface tension coefficient PyFluent
Fluent Eulerian multiphase drag law phase interaction settings
```

## Agent procedure when documentation is needed

1. Capture exact failing path, requested value, Fluent version, and solver mode.
2. Inspect live object children/options.
3. Search PyFluent docs for the setting object or parent object.
4. Search Fluent User Guide/Theory Guide for the GUI/model dependency.
5. Search Fluent Text Command List for TUI fallback.
6. Try minimal sandbox case before applying to the full case.
7. Record the successful path/order in `logs/successful_paths.md`.
