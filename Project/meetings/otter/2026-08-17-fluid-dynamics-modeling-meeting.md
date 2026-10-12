---
otter_id: "DnXULni5OV-Hu8PDOvJc5ls1xZU"
source_url: "https://otter.ai/u/DnXULni5OV-Hu8PDOvJc5ls1xZU"
source_start_time: "2026/08/17 14:58:29"
source_timezone: unspecified
imported_on: 2026-10-12
---

# Fluid Dynamics Modeling Meeting

| Field | Source value |
| --- | --- |
| Date and time | 2026/08/17 14:58:29 (timezone not supplied by connector) |
| Duration | 20m 54s |
| Source | [Otter recording](https://otter.ai/u/DnXULni5OV-Hu8PDOvJc5ls1xZU) |

Imported from Otter.ai. The summary and action items are Otter-generated; they record the meeting and are not verified project results. Original speaker labels and wording are retained. File dates use the timestamp supplied by Otter, without timezone conversion.

## Otter summary

Shuhei discussed his progress on the full geometry model with the bright outlet, focusing on convergence rather than just liquid cooling. He spent half of last week on geometry and meshing, running simulations with 1000 iterations. Scale residuals were unstable, and he tested different solvers, finding standard K-epsilon more stable. Shuhei faced challenges with the brine outlet pressure, affecting flux and convergence. Sadiq emphasized documenting all steps and results. Shuhei used polyhedral meshing for better accuracy, running simulations on a 230k cell mesh, and plans to increase iterations to 10,000. They also discussed the need for a water seal to prevent steam escape.

## Otter action items

- Grten3 . - grten2@gmail.com : Document all steps taken to attempt to stabilize and converge the CFD model (including turbulence models, relaxation factors, solver settings, and boundary conditions) in the project report, even if the final case does not fully converge.
- Grten3 . - grten2@gmail.com : Create a new CAD drawing of the full separator geometry based on Panonzo's dimensions and upload it to Drive so it is available for future reference and meshing.
- Grten3 . - grten2@gmail.com : Use the provided empirical correlation to calculate expected pressure drop across the separator and compare those values with the Fluent simulation results to validate the model.
- Grten3 . - grten2@gmail.com : Continue adjusting Fluent solver settings and initial/boundary conditions to achieve stable residuals in the full-geometry mixture steady-state model, targeting stabilization by next week.
- Grten3 . - grten2@gmail.com : After achieving stable residuals, investigate methods to maintain a constant brine outlet water level (for example, using a patched liquid pool and appropriate outlet control), and implement this approach in subsequent simulations.
- Grten3 . - grten2@gmail.com : Increase the number of iterations per simulation run to approximately 10,000 (from the current ~5,000) and re-run the relevant Fluent cases to better assess convergence.
- Grten3 . - grten2@gmail.com : Compile and organize all Fluent setup files, case configurations, and associated documentation in the report so they can be reviewed by the examiner and SSO.

## Full transcript

<details>
<summary>Show the complete speaker-attributed transcript</summary>

```text
[0:00:06] Shuhei: I made the full geometry again with the bright outlet, so with actual, so trying to get the the convergence rather than just liquid cooling at the bottom. So yeah, we're just working on the full geometry again, yeah. So rather than the simplified weights cut off at the, so I'm trying to do the brine outlet again. Yeah. So I spent like half of last week just trying to get the geometry and meshing right. So that was a lot of that was like most of the work actually, and then after that, I'm just I started running just mixture, just just trying to get it converge. But when I look at the scaled residuals, it's kind of like, as you can see, it's all over the place, right? So these are kind of different like setting experiments because flue has kind of guys on like because it's difficult to like stabilize. They have kind of guys on you should try out this this long. So I was just kind of trying it out, and I think so. These 1000 iterations like one checkpoint, and I think this was one of the better results. But I'm just trying to still like play around with settings and solver equations to try stabilize, I guess the residuals or epsilon and k values. You see, all
[0:01:31] Sadiq: all these steps you're doing, you document them in your report with results because it is it's a difficult model. It's a difficult problem, and just identify the steps you need to go through to get the model to converge. And even if it doesn't converge right at the end, you document all of this. Yeah, I do have. What model
[0:01:56] Speaker 1: is this? This residual is for which model?
[0:02:00] Shuhei: Like equation,
[0:02:01] Speaker 2: yeah. So
[0:02:02] Shuhei: this is all mixture steady, and with this is so this is with RNG K epsilon, and then this part is just simple, just basic RNG in the epsilon, but without like swirl and just standard wall functions, and just really like bare bones. So I'm just, just yeah, and then I can actually show you all the definition of the setups. But so I'm kind of just coming off on this. So in one meaning, so turbulence under relaxation humping, and
[0:02:35] Speaker 1: so you mean that you test a different solution solver, different solver, and the best one is K epsilon.
[0:02:44] Shuhei: So actually, it's this one. So just standard K epsilon. Yeah, and then and then so what Fluent suggested was just do standard K epsilon, and then once it's like stable enough, you turn
[0:02:58] Speaker 1: it back to the
[0:02:59] Shuhei: yeah. So that's kind of a little bit that I tried here, but I don't think I iterated it enough to because it's not actually really stable here. Yeah. But I think it does show a little bit of good sign. At least it's you know better than this. So I think I'll keep trying this more like basic route and then try get it to stabilize a little bit and then maybe switch it back onto a little more texture, and then some other things I tested actually before this is so because now we have the brang outlet, the the condition of the bray outlet is really important, right? So I was just testing a bunch of different pressures. If we can come back to see. Yeah, so I just kind of like test it out. So, although I don't, I'm not fully sure if I should even be using pressure outlet for brine outlet, constant pressure bonding. Yeah, but it's really difficult because when you change the bray outlet pressure, the the flux changes dramatically. Like if you if you put it too low, then the it doesn't the a lot of the vapor or the steam escape from the bray outlet. Whereas if you put it too high, then like a lot of liquid pulls up, and then the mixture steady can't find the steady or like the convergence. So I'm trying to okay from that I was like okay, so if when it pulls, like it kind of like goes into floating point error calculations and then just goes all over the place. So I was like okay maybe I should try transient solution rather than steady, but that's currently not working. So
[0:04:42] Sadiq: again, add you add so much complication if you go trans. Yeah, yeah. We are looking only in steady operation of that thing. But yeah, it's really difficult
[0:04:51] Shuhei: to even get the like steady. So it just just
[0:04:54] Sadiq: just for information, you know the the bottom of the the bottom of the heat exchanger has water somewhere here, and the outlet is somewhere here. So there is water, and that water is what we call it seal, meaning it prevents steam escape. Yeah. So water inside can go up and down a bit. That's fine, as long as doesn't let steam escape.
[0:05:21] Shuhei: Yeah. So actually, so that was just so when I was testing this pressure, it was just no initialized water pool. So essentially, no seal. So this is just straight up, just the vessel stuff goes in, and then there's brown outlet. There's no water yet. And then, secondly, I was like, okay, maybe I should initialize a pool of water patch, a pool of water first. But
[0:05:48] Sadiq: that-that was the old model was doing. It has like a where it sliced. Yeah, is that the water level? That's the assumption.
[0:05:55] Andy: Was the water level? Yes. But it's just that the the problem is
[0:05:59] Shuhei: water just keeps accumulating. Because there's no
[0:06:03] Andy: there's nowhere for water to go. Yeah, if with that model, but with the difficulty, with the old model, yeah.
[0:06:11] Sadiq: Well, it was disappearing at that ring, right?
[0:06:15] Andy: It's
[0:06:16] Sadiq: so the water was escaping here. That's its own laundry, but
[0:06:20] Andy: it's it's um it's modeled as a wall
[0:06:24] Sadiq: in the old one.
[0:06:26] Andy: So what happens
[0:06:28] Shuhei: is
[0:06:29] Andy: there's like the the basically water has has no outlet, so the the continuity residuals it doesn't.
[0:06:41] Speaker 1: mass. The last time you showed me, there is no continuity of the mass in your system.
[0:06:47] Shuhei: Yeah, yeah. I think I feel like we do. We can definitely. I feel like we can model the full model. Obviously, we haven't. I haven't really found too much success yet because. How
[0:06:59] Sadiq: does the geometry look like with that new model piece?
[0:07:02] Shuhei: should have a CAD model that I turned into all week. Is it
[0:07:23] Andy: in drive?
[0:07:25] Shuhei: Actually, I I didn't make the new drawing here. I can, I can quickly do that once I get back to that.
[0:07:32] Andy: I mean, it's just,
[0:07:33] Shuhei: it's, it's. I literally just copy and pasted all the dimensions. Yeah, and then From from the research paper that Panonzo wrote, he wrote all the like the dimensions and all the diameters. So I literally took that and then made that in the CAD. This is the one. Ah no, this is this is the simplified. This is just the simplified one. So it's cut off here, but essentially it's just this, but I added that. Yeah.
[0:08:05] Andy: So, literally, instead of cutting that off, we modeled that
[0:08:10] Sadiq: too. Yeah.
[0:08:11] Shuhei: And then if you if you scroll down a little bit, so I just took this. So this is the spiral inlet design that he specified. So I just took this and then made it with the one. So it shouldn't be what? Oh yeah, yeah,
[0:08:25] Andy: literally that.
[0:08:26] Sadiq: Yes, that's fair enough. Yeah,
[0:08:28] Speaker 3: yeah.
[0:08:31] Sadiq: By the way, the pressure drop calculation. There is an empirical correlation here to calculate pressure drop for for the mass flow rate, and you can compare your, which what you exchange is more or less yes, accurate, has a correlation for calculating pressure drop from in and out within the second. Okay.
[0:08:57] Andy: Yeah. Wait. So that the it's a small pressure drop. The liquid pooling at the bottom,
[0:09:03] Sadiq: yeah, is
[0:09:04] Andy: that that depends on the the pressure of the brine outlet.
[0:09:09] Shuhei: Well, this this is there's another component that keeps the water level, right? If I'm for the brine,
[0:09:18] Andy: like how like in a real separator, how would you control for the water level, or is that not something that you do?
[0:09:30] Sadiq: Because it's a complex system to control water level. It's basically to the they throttle the water outlet, but because the operation of the separator is not 100% steady state, because the fluid coming from the well can go. The well has a mind of its own; it can go up and down as it chooses. So they throttle the outlet of water, but small change. I'm talking about small change, and that's all the water level inside. Inside the separator, so there is like a here.
[0:10:12] Shuhei: Yeah, that's also what I'm a little bit. There's there's
[0:10:15] Sadiq: more like a sight glass. See, this is water level inside a sight glass, and there's a detector here. Detector, you can see water level going up and down slightly, and there's detector here, pressure detectors here. And once the water drop slightly within, the throttles the valve here. This is connected to valve and pumps, and the pumps change about because the operation, because the the two-phase fluid coming in can vary in pressure slightly, slightly, and that to control that to make sure there's always water here, which is the seal, so that steam doesn't escape with water, and all these things go up and down. So, yeah, but again, because the operation is not 100% steady, and this is where they have their control and the transient. But in our case, we don't need to model that small change. That's playing around in the flow. We don't need to worry about. We just
[0:11:20] Andy: set that as a constant. Yeah. So,
[0:11:22] Sadiq: assume the water level is fixed, or semi-fixed, or yeah, in a in a steady operation.
[0:11:29] Shuhei: Right. Yeah. Yeah. It's just. Well, when I was when I was patching it, I I still haven't looked into it too deeply since obviously I haven't even got the disk to stabilize, so maybe because this is at the moment with no patched initialized water pool, so I could try, but yeah, even if I patch it, it just it it doesn't really change because it's equations. So once I figure that out, obviously I can do the hatching and stuff, but yeah, because when I when I drop the pressure at the outlet, or when I increase the pressure at the outlet, obviously more water pulls up at the bottom, but it just keeps pulling up, and then it'll. I think I'll need to have some function at the outlet so that it knows how much water level there is pulling up, but also yeah, I mean there's quite a bit of uncertainties. If I initialize it, the solver runs into an error quite quickly, and then when I try to do so, when I try to do no no initialized pool, and then runs it run it for a few 1000, I don't know, a couple of 1000 iterations, and then patch it, and then change the pressure a little bit to match the because now it's pull, so the dry outlet pressure would change. But then when I do that, I haven't really figured out how to, because because the flow field is already quite different to, I think when it would be when it's initialized, it just runs into an error. So yeah, so even if I do it first, solve it without the pool to solve the flow first, and then you just patch the fluid at the pool, and then sort of like just runs into an error. So I need to kind of figure out the transition. Yeah, or just completely start from the patched pool, but that hasn't really succeeded for me either. So I'll keep looking into other like how effluvium suggests how these model like soil-dominated cyclone things are modeled, and hopefully get this to first stabilize, and then look into keeping the brine level constant. Yeah. So yeah, for for now the definitely the number one goal is to try get the residuals to stabilize, and then we can try figure out how the grine can stay constant.
[0:14:15] Sadiq: So the the report you put, yeah, these these contours. What do they do?
[0:14:26] Shuhei: Yeah. What's what's what's red and blue? So so blue is where like where there's very little or essentially no legit
[0:14:37] Speaker 1: level. Where is the legend? Oh, I I I
[0:14:41] Shuhei: had to cut it out to fit all the four, but I do have I do have um I do I do have the full pictures.
[0:14:48] Speaker 1: You don't have 344, right?
[0:14:50] Shuhei: No, I didn't take three four. You had
[0:14:52] Speaker 1: in the 340. but no, I mentioned that if you are going to put it on two, you need to have something. Well, that was more for.
[0:15:00] Shuhei: I do have the full images though.
[0:15:01] Sadiq: Yeah. Yeah. So the red meaning west, blue, dry. Yeah. Simple. So
[0:15:06] Shuhei: yeah, but these parts are kind of like
[0:15:09] Sadiq: mixed.
[0:15:09] Shuhei: Yeah, mixed. I mean, this is like a computer. Yeah, but but also yeah, that's the simplified model stuff. But it kind of does show the rough behaviors, I guess.
[0:15:22] Speaker 4: Yeah,
[0:15:24] Sadiq: yeah. For this one, this one is old because no, this is actually reasonable. But those patches are very. Yeah, it's really strange. Strange. I mean,
[0:15:36] Shuhei: also yeah. Since that meshing is like four petrochem, the new with the full geometry that I'm working with. Okay. Anyways, I'm using poly hex to mesh the new ones rather than just regional, and I think that's actually giving much more accurate ones because there's more like layers at the outlet where that's where most of the liquid is, and that's where most of the I think the complex interactions are happening. So I think this is actually even though it's some of the meshes that I'm running are much coarser course, I think it's actually giving more accurate results. So I think that's also really good as well.
[0:16:21] Speaker 1: How long does it take to run with the mesh?
[0:16:25] Shuhei: Well, I've kind of created roughly three meshes where one of them is just around really close, so like 230 k cells, and then other ones 600k, and then the other one's nearly a million. With I'm just really because like I'm, I haven't even got the fundamentals on the solvers. I'm just testing it on a really coarse one. I don't know if that's a good idea, but so I'm just using the 230k cell mesh right now. That's like for 1000 iteration. I think it's like less than 20 minutes. Okay. Yeah. So it's pretty quick, and yeah, and then because it's really coarse, I can use my home computer and use the student version. So that just sped up the experimental fit. Do
[0:17:11] Sadiq: you think it's worth my get to use the IC with a very fine grid, or
[0:17:17] Speaker 1: but even with 1 million mesh, they can use obstacle even with.
[0:17:31] Andy: Do you know if there's a chance that we can install like Team Viewer? Yeah, just so we can control the computer from home. Yeah, yeah, remote.
[0:17:41] Speaker 1: Yeah, remote computer is just available for postgrad and PhD students for part four.
[0:17:47] Shuhei: Is there any like fluent computers that we? Remote
[0:17:49] Speaker 1: computer means that they they give you some. They even access a username, password, and then allocate the space around the space memory and install your required software in your remote computer, it doesn't mean that you can view your, for example, one of the PC ups there. Is it totally different? You you want to see your upstairs PC, right?
[0:18:18] Andy: Yeah,
[0:18:19] Speaker 1: it's something else. Like if I can just. My own
[0:18:28] Shuhei: laptop. Yeah, yeah. No, it would just speed up a lot more if I could do more
[0:18:42] Speaker 1: at home. you don't have Ansys in your computer.
[0:18:45] Shuhei: At my home computer desktop, I do have Ansys student version. Yeah. So with that one student
[0:18:51] Speaker 2: version, you can run your course. Yeah, that's what I'm using. Yeah.
[0:18:57] Shuhei: And then my version
[0:18:58] Speaker 2: computer to run your simulation.
[0:19:00] Shuhei: Yeah, that's the idea for now. But yeah,
[0:19:05] Sadiq: limitations,
[0:19:06] Shuhei: limitations. Yeah, I'll try hopefully get this stabilized by next week, and then maybe work on the patching and trying to keep the prime. Normally,
[0:19:17] Speaker 1: we use at least 10,000 iterations with this sort of. Okay. Okay. Yeah. Cause yeah, maybe it's too little iteration. I wasn't too sure
[0:19:26] Shuhei: how many iterations I should be doing. I'll I'll definitely run them more longer. Okay. Okay. I'll do I'll do around 10,000 here because it runs
[0:19:36] Speaker 2: for now around five and then okay yeah because I can
[0:19:40] Shuhei: run them fairly quickly so it shouldn't be too big a game issue.
[0:19:44] Andy: Do you have any other suggestions for this? I feel like the team
[0:19:50] Speaker 2: didn't get the convergence. You don't know if your result is correct or not.
[0:19:55] Speaker 1: That's why the first step is to get the coverage, and then then you get the result and refine your mesh.
[0:20:03] Sadiq: I I don't want you to stress even reporting all the steps you take.
[0:20:08] Shuhei: Yeah, I do have everything. All the setups, all the cases,
[0:20:12] Speaker 1: justify your estate, your examiner, and SSO, whoever can be. Yeah. Then make sure that
[0:20:22] Sadiq: Coming up with a model that perfectly matches what we expect is it's okay not getting there. Yeah. Okay. I mean, I do want to get there, but yeah. Of course, right. But even so, even so, we can document the steps and show where the problems are, and
[0:20:49] Shuhei: yeah, okay, yeah. I guess that's it for today. Yeah.
```

</details>

