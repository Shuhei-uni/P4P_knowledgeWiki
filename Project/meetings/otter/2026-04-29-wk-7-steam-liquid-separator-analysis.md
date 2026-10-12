---
otter_id: "q8tXwcoMU8edib-KuU0_50isBB0"
source_url: "https://otter.ai/u/q8tXwcoMU8edib-KuU0_50isBB0"
source_start_time: "2026/04/29 19:05:54"
source_timezone: unspecified
imported_on: 2026-10-12
---

# Wk 7 - Steam-Liquid Separator Analysis

| Field | Source value |
| --- | --- |
| Date and time | 2026/04/29 19:05:54 (timezone not supplied by connector) |
| Duration | 14m |
| Source | [Otter recording](https://otter.ai/u/q8tXwcoMU8edib-KuU0_50isBB0) |

Imported from Otter.ai. The summary and action items are Otter-generated; they record the meeting and are not verified project results. Original speaker labels and wording are retained. File dates use the timestamp supplied by Otter, without timezone conversion.

## Otter summary

The team discussed the replication of results from a 2013 paper, focusing on the spiral inlet and steam-liquid separation. They noted discrepancies in steam quality, with their model showing higher values than expected. The k-epsilon model with default parameters was used, but its accuracy is uncertain. They proposed adding a chemical tracer to track liquid movement and suggested modifying the geometry to include a bottom pipe for better accuracy. Andy highlighted the need for detailed parameters missing from the original paper. The team agreed to continue testing and refining the model to match analytical results and improve the separator design.

## Otter action items

- Speaker 0 - : Email the specific file name to the contact energy person so they can send the corresponding file.
- Speaker 0 - : Implement a chemical tracer in the simulation to track liquid droplets and see how much liquid travels with the steam, coordinating with the team member who will look into the injection details.
- Speaker 0 - : Run systematic parameter sweeps (for example, k-epsilon model parameters) and compare the resulting graphs with the analytical solution to perform a sensitivity analysis.
- Speaker 0 - : Design a full separator geometry that includes the bottom section and a water outlet pipe, and define appropriate boundary conditions for the water exit based on hydrostatic pressure.
- Speaker 1 - : Obtain data and design for a real separator from contact energy so the team can match the simulation results against real-world data.
- Speaker 6 - : Investigate how to implement the tracer injection (for example, using fake particles) in the simulation and report back on the approach.

## Full transcript

<details>
<summary>Show the complete speaker-attributed transcript</summary>

```text
[0:00:02] Speaker 1: It doesn't have to, like the geometry and everything, so it has, like a one of the files have a path that leads to another file, but that
[0:00:14] Speaker 2: that email me the name of the file, yes, and I'll pass the guy to send.
[0:00:20] Speaker 1: Okay, yeah. But for in the meantime, I've just, I had, like, I made it because the sketch was already there on the bang one. I quickly made the spiral inlet from the sketch. And kind of just being working with that, and he's doing like, kind of like the validation, and I'm just
[0:00:42] Andy: not validation. But like, No, I'm still trying to replicate the the result from the 2013 paper.
[0:00:50] Speaker 1: Yeah, but it's taking quite a bit longer than we expected. So while he's doing that, I'm just kind of like playing around with the new, new setup, which can,
[0:01:01] Speaker 3: can they run it? Yeah, it's fine for the computer, the lab computer. Yeah, it's okay. The lab is okay for now.
[0:01:22] Speaker 1: So I've just been kind of playing around with the spiral in there. And then I set up where you were telling us last time about,
[0:01:30] Speaker 2: like, separating. So this is steam. This is liquid, yeah.
[0:01:35] Speaker 1: And I'm not too sure what's happening here, because, like, the because this is the
[0:01:38] Unknown Speaker(s): velocity vector, this water is
[0:01:41] Speaker 2: coming too slow. Yeah, what is they normally come roughly the same.
[0:01:45] Speaker 1: It should be, it should be the same, but I need to fix up what's happening here, because it should be somewhere, but it's the same.
[0:01:55] Speaker 2: The water enters roughly the same velocity. Steam might be, still slightly higher. They call it slip ratio, where the steam slips on water slightly, but at the inlet, assume it's more or less the same velocity. It will slow down. Inside the separator, steam will still travel fast, but water will go down and
[0:02:16] Speaker 1: yes, so I'm just kind of kind of like modeling and seeing how it was, but the most of the Yeah, and actually, we're still confused with quantum, because this is like the PowerPoint of the particles, but I think it goes back off. Yeah, I'm just
[0:02:44] Speaker 2: I've seen the steam as it enters into the pipe. The steam is spinning right, spin, spin. And when it enters the pipe, it's still spinning. It has the same spinning action because minerals that carry it put them in a spiral. I can see that visually once, once they open and take pictures of the inside. So the steam, spin, spin, go inside the tube and still continue that spin slowly, and then the spin disappear.
[0:03:14] Speaker 4: I'm just wondering which model, which model did you apply in the answer?
[0:03:20] Unknown Speaker(s): So this is the model. That's the mixture. I mean the physics, physics,
[0:03:27] Speaker 1: yeah, k epsilon, with just the normal mixture. It's, it's all the, all the ones,
[0:03:35] Unknown Speaker(s): RNG, we just based
[0:03:38] Speaker 5: it off. And how did you define those parameters, that is just a default parameter you got from somewhere.
[0:03:44] Speaker 1: We got it from, and then we're not 100% sure if these parameters are right. So that's why he's so while I'm kind of playing on with the geometry, he's playing with the parameters. So once he finds like something new with the parameters, and you are
[0:04:01] Unknown Speaker(s): kind of comparing
[0:04:04] Andy: your values with this paper. Yep, sorry. Now, so this paper, as we're doing it, we found that there's actually a lot of like details missing. So say the like, all the parameters in the say the RNG, k epsilon model, like, there's, there's no mention of that, so it's just, I've just left that as default. And then another issue I think I asked you about this last time is how he modeled, how he scoped this program, which I mean, like it makes sense, but the way you model it, I feel like it's kind of difficult. So basically what happened is, like, we only care about the steam, right? So he just, he scoped it by assuming just cutting that there, so assuming that the water level is constant. So that's actually not model. So it's just like that, just like a
[0:05:01] Speaker 2: constant pressure boundary where everything disappeared, yes, but
[0:05:05] Andy: the issue with that is, if I made that, if I turn that into an outlet, like a pressure outlet, same as this outlet, all the all the steam which has come out of there as well. All of
[0:05:23] Speaker 6: them, all of them go down. Everything goes down, nothing go up, yeah.
[0:05:27] Andy: But like, in the assumption, right? What should happen is, like, if that's constant level, then the steam should, like, bounce off that type thing, right? And then it spins up, but you can't so basically, I'm pretty sure what he did in this paper is he just made that a a boundary, like, like a wall boundary. So what ends up happening is you actually don't have conservation of mass, so because the liquid has nowhere to go, so the steam goes out there, but the liquid has nowhere where to go. So like, Yeah, I'm not sure what's going on with that. I guess the volume, oh, I guess this kind of tells
[0:06:14] Speaker 1: you, but when we look at the volume fashion, if we just do this part, we just see, we don't see much at the bottom. It's just kind of spread out everywhere, or like, just everywhere, because it keeps, kind of, like stay, I think the water, even if it goes to the bottom, it gets spiraled up again, because it has
[0:06:34] Unknown Speaker(s): nowhere to go.
[0:06:36] Speaker 2: Yeah, maybe we should include the bottom part and have the pipe at the bottom that you just showed as an exit. Maybe have because water level normally somewhere here, okay, and they just accumulate and we take the water from here, or sometimes somewhere here, water level here and and water leaves here and let it go down and accumulate.
[0:07:08] Speaker 1: Yeah, yeah. I did quickly. I didn't make the geometry for this as well. Without the we could quickly test it out and see the differences.
[0:07:22] Speaker 2: I'm trying to get up to contact energy, I'm trying to get data and design for a real separator that's having a problem, and we have the data for that. So are we getting approval? And if we get that, then you have a real design with the real data that we can match, and they'll be great. Yeah, great. What you're doing is keep doing this for now, so get familiar, and if it's changing different equations for solving different models. I don't know this is what he used at the time. Yeah, maybe there's something better that's super turbulent, as you can see, and it's not
[0:08:22] Unknown Speaker(s): easy, so I guess we'll just try
[0:08:25] Andy: match the result. Should I? Should I still keep trying this? Like, I mean, I've, I've managed to run through like, half of the cases so far, but basically, our steam quality is coming out a lot higher than than what he's getting. I'm not sure what's going on there, too. So you're
[0:08:48] Unknown Speaker(s): just kind of testing out, yeah.
[0:08:50] Andy: So the the worst case, which is, like, here, right? I'm getting, like, there, and then the rest is just straight up, like, 100% can't be right. So do you think I should keep, I should try all that just for the sake of, like, I don't know, completeness, and then maybe we can switch to actually modeling the outlet, the water outlet,
[0:09:28] Speaker 2: so the dots are his model, right? Yes, the red one analytical, yeah,
[0:09:35] Unknown Speaker(s): the red one, his one.
[0:09:38] Speaker 2: They're showing that. It's way worse.
[0:09:41] Speaker 3: Yeah, his one showing was, yeah,
[0:09:44] Unknown Speaker(s): still high, by the way, but still, and you can't get that. You can't match, no, I can't
[0:09:53] Andy: my ones, my one show is closer to the analytical, not sure what's going on. Going on. But, yeah, I mean, I'm thinking because he left like details, like parameters, out of his paper too. So maybe, maybe he changed something I didn't.
[0:10:22] Unknown Speaker(s): So that's that, yeah, so
[0:10:26] Speaker 2: when you're running, are you getting similar with the motif, with the different inlet?
[0:10:32] Unknown Speaker(s): Oh, well, with the different
[0:10:35] Speaker 1: inlet, he does like more, I guess, different graphs. But you know, at the moment, I'm not really double checking with these. I'm just letting him do the parameter
[0:10:46] Speaker 7: stuff to just duplicate the first graph. Once you're comfortable with the model, you can just change the geometry.
[0:10:53] Speaker 5: Can you but your your data is more aligned with the analytical and the calculation one, right?
[0:11:00] Speaker 2: Yeah, that's good. Can you add a tracer? A tracer to see where it's going the liquid. Because the tracer will go only with the liquid, not with steam, and if any droplets of water go with the steam, you'll be able to track them, okay.
[0:11:24] Speaker 1: So add okay. So try and track every detail of the actual water droplets.
[0:11:29] Speaker 2: Is no no. So, like a chemical tracer, when you have water and steam, but you can have a, have a tracer, like a chemical, like, okay, like some, like a paid particle or something,
[0:11:43] Speaker 6: fake particles, yes, what is that injection? We'll look into that. Is that different?
[0:11:50] Andy: That's different to a water droplet injection, right?
[0:11:53] Speaker 2: Yeah, no, no, not washing. This is a chemical tracer like because when you do modeling, you can have the liquid, the liquid also, you can have chemicals also, concentration of something, all right, so if we can take these chemicals, stay with the liquid only, doesn't go on to the steam. There are chemicals go to the steam of the liquid. So this way, we want to see where, how much of those chemicals that go in water travel with the steam. Can
[0:12:31] Unknown Speaker(s): you do for, for,
[0:12:33] Speaker 7: for example, if you want to change what, what approach Are you following, sensitive the analysis right? You're doing parameter sweeps to see how sensitive is. Your output compared to this one, it would be good if you can, you know, compare those graph together. If you are, for example, changing parameter for k epsilon, then you know, compare those graph and then compared with the simulation,
[0:13:04] Speaker 5: yep, is it kind of systematic? Yeah, yeah, make sense.
[0:13:19] Unknown Speaker(s): Send me the name of the file. Oh, yeah, specific, which, and I'll send it. Yeah.
[0:13:35] Speaker 2: Let's focus on a full separator. We'll find another boundary condition for the water exit, because the water will have higher hydrostatic case, so the pressure coming out will be slightly higher.
[0:13:58] Unknown Speaker(s): Since.
```

</details>

