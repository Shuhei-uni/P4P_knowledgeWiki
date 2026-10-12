---
otter_id: "zY1gXxBmQrSLrp4seHZj_MNUKoA"
source_url: "https://otter.ai/u/zY1gXxBmQrSLrp4seHZj_MNUKoA"
source_start_time: "2026/05/20 19:03:27"
source_timezone: unspecified
imported_on: 2026-10-12
---

# Fluid Dynamics Modeling Meeting

| Field | Source value |
| --- | --- |
| Date and time | 2026/05/20 19:03:27 (timezone not supplied by connector) |
| Duration | 27m 53s |
| Source | [Otter recording](https://otter.ai/u/zY1gXxBmQrSLrp4seHZj_MNUKoA) |

Imported from Otter.ai. The summary and action items are Otter-generated; they record the meeting and are not verified project results. Original speaker labels and wording are retained. File dates use the timestamp supplied by Otter, without timezone conversion.

## Otter summary

The team discussed challenges in modeling a two-phase inlet system, focusing on a test setup with velocity inlet for water and steam. Issues included convergence errors, water pooling, and turbulence at the outlet. The outlet geometry was debated, with suggestions to refine it. The inlet condition was critical, with a focus on separating steam and water phases. Metrics such as mass flow rate and enthalpy were discussed, with a need to ensure steam quality. The team agreed to simplify the model, focus on inlet conditions, and track droplets using tracers to improve the model's accuracy and reduce water contamination in the steam.

## Otter action items

- Andy - : Inform the assistant about the email regarding the research paper so that the paper can be located and shared with the team.
- Speaker 3 - : Update the Fluent inlet boundary condition so that steam and water enter as separate phases (water on the outside, steam on the inside) instead of a homogeneous mixture, and run simulations with this inlet setup to study its effect on steam quality and carryover.
- Speaker 3 - : Reduce the pressure at the brine outlet in the Fluent setup to prevent flooding and stabilize the water level at the bottom of the separator.
- Speaker 3 - : Bring and share contour plots and other visualizations from the current Fluent simulations at the next meeting for review.
- Speaker 3 - : Ask the advisor about appropriate Fluent solver settings (including whether to use energy, mixture model, and turbulence model) for the two-phase separator simulations.
- Speaker 3 - : Measure the steam outlet geometry from the figure in the research paper using a ruler to obtain approximate dimensions for the Fluent model.
- Speaker 3 - : If the current water-pool initialization method cannot keep the water level stable at the bottom, revert to the previous initialization approach used in earlier simulations.
- Speaker 4 - : Send the Fluent case files for the 2566-iteration and 4000-iteration simulations to the team via Google Drive.

## Full transcript

<details>
<summary>Show the complete speaker-attributed transcript</summary>

```text
[0:00:04] Andy: Yeah,
[0:00:06] Speaker 1: but in terms of, I guess, what I did, or what we did, I had a test yesterday as well. So, for the past, like, a week, I've just been, or two weeks, I guess, kind of studying for the test, and I haven't, I haven't really made progress, but I did do the two phase inlet, and then at first I was setting it as just like normal volume, just like water, and then steam, which messed up with the velocity, so I changed it to velocity inlet, so both of them actually goes in at the same velocity,
[0:00:42] Speaker 2: yeah,
[0:00:44] Speaker 1: yeah, but I came across quite a bit of like convergence errors, or like it just didn't really converge, also with when I initialized, because now I'm working with the full model with the Brian outlet as well, because earlier we were
[0:01:03] Speaker 2: with
[0:01:04] Speaker 1: a slice, but now we added the brine outlet, like the bottom part, and then I also initialized the water level of the slice, or like from the slice to below, but I think it's to do with how I set up, set up the fluent, but when I, whenever I run it, it's just like the pool of water at the bottom, after like more iteration, just like combines with the steam, and just like spiral, yeah, exactly, so I haven't been able to like figure out like a reason or like a solution to that, but
[0:01:39] Andy: what's the
[0:01:42] Speaker 2: lower exit look like,
[0:01:44] Speaker 1: it's just I'm not sure if Andy, I'm sure he has the research paper, it just looks like just a circle, circular tube coming out from the die, and I don't think, like I'm questioning if that's the right geometry, because, because it doesn't do a very good, like, there's a lot of turbulence at the output here, yeah, sometimes when the file is big, from it separates into a couple of zip files,
[0:02:35] Andy: yeah, yeah. Yeah,
[0:02:48] Speaker 3: sorry, sorry, yeah, the
[0:02:52] Speaker 1: outlet looks like so, so the bottom part just like is like a like a bowl, and then the outlet just like
[0:03:00] Speaker 2: a hole through,
[0:03:01] Speaker 1: yeah, just the hole through the side,
[0:03:04] Speaker 2: yeah. And what's the boundary condition there?
[0:03:07] Speaker 1: So just a pressure outlet here.
[0:03:11] Speaker 2: What's that pressure
[0:03:12] Speaker 1: at? It's the same as a steam outlet pressure, which is so the inlet was 11.4 bar, yeah. And then what, 11 points for something passing,
[0:03:24] Speaker 2: you put the same thing,
[0:03:25] Speaker 1: yeah, and then no outlet is just lower, so 11.2 for out both of the outlets,
[0:03:33] Speaker 2: and that was not enough to clear the water when the water builds up and flood.
[0:03:38] Speaker 1: Oh, actually, so with the operation, and then there's like operational pressure, right, for Fluent. So I guess the entire.. I might have said that to
[0:03:51] Speaker 2: let's go get mine while we're getting
[0:03:54] Speaker 1: the, yeah.
[0:04:50] Speaker 2: Oh, she's out there.
[0:04:51] Speaker 1: She's not there. Yeah, we'll make sure to message the chat next time to make it make it clear.
[0:04:59] Speaker 2: So you said for the next two weeks, which is you guys are exams. I thought this week you were coming, but that's all right. I'm here. I wanted, I saw her this morning, and told her they said not coming. Yeah,
[0:05:15] Speaker 1: yeah, sorry, yeah, no, that's that's our fault for not communicating well. But yeah, but overall I'm just a bit confused on, I guess, the direction of it, because, because there's so many things that I guess we could do, yeah, but to test out each possible thing, it takes so much time that we obviously can't do everything, and I'm not, because I don't, I'm not 100% sure, which would give us, like, I guess the best results. So, because I might test something, and then it would be, it would, it wouldn't like the result could be very bad, and
[0:05:57] Speaker 2: I think the main thing is assuming it's not homogeneous mixture,
[0:06:01] Andy: yeah,
[0:06:02] Speaker 2: and change the inlet condition,
[0:06:04] Speaker 1: yep,
[0:06:05] Speaker 2: and see what we separate steam from, like you showed last time, there's some water, that's the approach, and we want to see how we can get the model to perform that way
[0:06:18] Speaker 1: here, okay, so just
[0:06:21] Speaker 2: rather than using a homogeneous, we're using two separate
[0:06:25] Andy: fluids. The
[0:06:27] Speaker 2: inlet is is a bit separated, not a mixture.
[0:06:31] Speaker 1: Yeah, yeah,
[0:06:33] Speaker 2: that's the approach we want to take, because fluid enters, that's why it's spiral, because the fluid come up goes there. in that process. The water is on the out and the steam is on the in, and they in turn start spinning. Steam go up, water go down.
[0:06:52] Speaker 1: Yeah, yeah. Well, yeah, I was able to, I guess, successfully model, model that part, I guess,
[0:06:59] Speaker 2: with the old boundary condition or the new
[0:07:02] Speaker 1: one. What do you mean by
[0:07:04] Speaker 2: the bottom exit
[0:07:06] Speaker 1: with the bottom exit? Yeah, with the bottom exit. I did the spiral with two phase
[0:07:12] Speaker 2: with the old bottle exit or with the new one that you did
[0:07:15] Speaker 1: with the new
[0:07:16] Speaker 2: one. Okay,
[0:07:17] Andy: yeah, but
[0:07:19] Speaker 2: the way we judge the model is working is the no water going with the steam. How was the quality of the,
[0:07:27] Speaker 1: yeah, so that's where the issue kind of, I guess, lies. The when I look at the mass flux of the from the inputs and the outputs,
[0:07:37] Andy: yeah,
[0:07:38] Speaker 1: there is still like it doesn't match up.
[0:07:42] Speaker 2: Yes,
[0:07:43] Speaker 1: yeah. So I was, I was like, I don't know, maybe I'm doing something wrong, because
[0:07:48] Andy: it's
[0:07:48] Speaker 2: what's the difference. They should this, if should have called this and plus this, right?
[0:07:53] Speaker 1: Yeah, for for liquid it was around like 50 was coming out, even though, like, so he was like negative 50 kilograms per second.
[0:08:09] Speaker 2: How much steam?
[0:08:11] Speaker 1: So, what?
[0:08:12] Speaker 2: How much steam
[0:08:13] Speaker 1: for the steam? It was almost converged, I guess. It's just a liquid that was like that was like there was more coming out, even though there wasn't like going in.
[0:08:25] Speaker 2: How much total was going in
[0:08:28] Speaker 1: both? I need the research paper for that, but it should be, it should be with the 1600 joule or kilojoule, yeah. Enthalpy, and then with that, we, you get the, I guess, the velocity, I think
[0:08:44] Speaker 2: mass flow rate,
[0:08:45] Speaker 1: yeah, mass flow, and through that, I think I calculated, but I'm sorry, I didn't bring my laptop here, but it should be, it should be the amount, let me, let me see if Andy has the research paper, and then I just, I just based the number off that, so, so the in inlet should be right, because I just like the, the mass flow, and everything is just based off the past research paper, and that seemed to get fairly accurate results, I guess, yeah. yeah, I,
[0:09:26] Andy: I'm not sure.
[0:09:29] Speaker 2: The let me get a piece of paper on
[0:09:33] Speaker 1: worries.
[0:09:53] Andy: Hi, I know. I think I need to go, and I just like to sleep. One,
[0:10:00] Speaker 4: I saw the email was nice.
[0:10:04] Andy: I'm glad. I'll tell my assistant,
[0:10:09] Speaker 2: so right water here under two phase M dot Steam dot water drawing whatever water and this X, which is dryness fraction, is based on enthalpy. Okay, so x equals enthalpy, which is h of n minus enthalpy of liquid at separation pressure divided by hfg at separation pressure from your steam table.
[0:10:56] Andy: Okay, yeah,
[0:10:57] Speaker 2: did I give you steam table?
[0:10:58] Speaker 1: Yeah, yeah, you did. Yeah,
[0:10:59] Speaker 2: okay. We get x and m dot steam equals m dot total x, and this one is just the difference. So we need the mass should be, but the thing is that with the steam? There are some droplets of water going,
[0:11:21] Speaker 1: yeah, yeah, yeah. There was actually, yeah,
[0:11:26] Speaker 2: that's the magic. This is, yeah, and this is what we want to know. Let's calculate the efficiency of the separator equals m dot steam dry steam divided m dot steam plus m dot b, which is those plus m dot brine or carried over drop. Yes, and that gives you efficiency of the separate,
[0:11:59] Speaker 1: yeah, yeah,
[0:12:01] Speaker 2: as in the paper,
[0:12:04] Speaker 1: yeah,
[0:12:05] Speaker 2: so so that you don't have to go and repeat as many, we want to try to see what changed the inlet condition to see when we're going to see carry over or no carry over, or what's the actual efficiency when we have that kind of inlet boundary condition rather than a homogeneous mixture of steam and water, which is not real.
[0:12:33] Andy: Yeah,
[0:12:35] Speaker 1: yeah, I kind of, I guess, briefly, I'm not fully, like, 100% understanding, but my confusion is that because I think I did the inlet and the outlet fairly, or I guess set it to like an okay point at the moment, it's just that I'm not too sure how to do like the like the silver setting, so for example, like there's like like energy, or like there's the mixture, could be based off of like RNG K Epsilon, like this, there's so many settings like
[0:13:14] Andy: that,
[0:13:15] Speaker 1: and that's where I'm most confused about,
[0:13:20] Andy: okay,
[0:13:21] Speaker 2: that's more,
[0:13:22] Speaker 1: more hurts, yeah. Because that's where I was, like, I guess, most confused on, because, yeah, I wasn't too sure, like, because you, when you change one of the settings, it could drastically change the output, and it could,
[0:13:39] Speaker 2: yeah. Yeah, part of it is you try different solvers.
[0:13:46] Speaker 1: Yeah,
[0:13:47] Speaker 2: so I have nothing against trying different solvers. It just, you wanted to kind of confine the problem, right?
[0:13:55] Speaker 1: Yeah, because there's so much,
[0:13:57] Speaker 2: so much things
[0:13:58] Andy: over
[0:13:58] Speaker 1: setting, so like inlet, like in the geometry, like everything.
[0:14:02] Speaker 2: Yeah, we focus on the inlet,
[0:14:06] Speaker 1: just inlet, yeah. Okay,
[0:14:09] Speaker 2: making a way that the inlet is separate phases, going water on the outside, the spiral, and steam on the inside, and then try to try different scenarios, and with that setting, try different silver to get us to give us the best possible
[0:14:30] Andy: bit of
[0:14:38] Speaker 1: workout. out, I'm doing this right, right, yeah. It started.
[0:14:50] Andy: Yep.
[0:14:59] Speaker 1: Yeah, I think when you download from Google Drive, like it separates it from into like separate zip files, because the file is so big. If you could just
[0:15:22] Andy: Yeah, no worries, I How's that nice? That was okay. Okay, if it
[0:15:52] Speaker 2: has divided it into multiple copy those, because everyone comes at a different size,
[0:16:01] Speaker 1: yeah, perfect.
[0:16:16] Speaker 2: Each has a different size. This is, yeah,
[0:16:18] Andy: so it's distinct,
[0:16:20] Speaker 2: different size. Okay, the files name might be the same, zip one, zip two, zip three.
[0:16:26] Andy: Yeah,
[0:16:28] Speaker 2: hopefully it's not the same thing.
[0:16:30] Andy: Yeah, it's okay if it's just beautiful. Let's see if this is different. The case file,
[0:16:53] Speaker 1: if you could give us both of the 2566 iteration, and the 4000 Yeah, perfect. Okay,
[0:17:08] Speaker 2: yeah, okay. That's all I can see.
[0:17:11] Andy: Oh, yep, yeah. Was that
[0:17:15] Speaker 1: zip files?
[0:17:20] Andy: Oh,
[0:17:22] Speaker 1: I think this
[0:17:24] Andy: is that you can cancel that. Cool. Thank you so much.
[0:17:32] Speaker 2: I was talking about the size of the project, we don't want to keep going, and the main difference, new work from the previous work, is the inlet condition, the two phases enter together, separated, not mixture,
[0:17:59] Andy: so I mean, currently, have you talked to him about how you're trying to model the,
[0:18:05] Speaker 1: yeah, yeah, the water initializing the with the actual water, like without the..
[0:18:10] Andy: so should we keep going with that?
[0:18:12] Speaker 2: Yeah,
[0:18:13] Andy: that's that's okay.
[0:18:14] Speaker 2: Yes, okay. I mean, if you're getting flooding, yeah, keep reducing the pressure there.
[0:18:23] Andy: Okay, so
[0:18:24] Speaker 2: outlet pressure reduce it a bit more, okay, till till we reach a balance,
[0:18:30] Speaker 1: okay, okay, okay,
[0:18:32] Speaker 2: where the flow water level stay the same at the bottom, because we model it steady state, we're not doing transient,
[0:18:41] Speaker 1: yeah, right, yeah, yeah, yeah, yeah, that was the issue, yeah, I guess I kind of had, yeah, even though it was a steady state, it acted as if it's a
[0:18:51] Speaker 2: transient, should kind of reach stabilizing, because that separator runs like this all the time, when it started up and shelled, not interested in that transient effect, we want to make sure it's running steady state all
[0:19:11] Andy: the time.
[0:19:13] Speaker 1: Also, one other thing that I was actually, I just realized, confused about was with the from the research paper, they don't really have like the geometry for the the steam
[0:19:26] Andy: outlet,
[0:19:27] Speaker 2: the
[0:19:28] Speaker 1: outlet here, and I wasn't too sure, like, because there's like a
[0:19:33] Speaker 2: live corn shape,
[0:19:34] Speaker 1: yeah,
[0:19:34] Andy: yeah, we just eyeball it right now,
[0:19:38] Speaker 2: okay. Okay, okay, let's run with it, you know. Yes,
[0:19:44] Speaker 1: okay,
[0:19:46] Speaker 2: you can kind of measure with the ruler, the figure.
[0:19:52] Andy: Okay,
[0:19:53] Speaker 2: let's do this. Okay, cool. Well, magic is the. Is they should enter at two separate phases already. They go inside, they might mix a bit, and steam go this way. We are interested, you see, what happens is on the walls, because steam going this way and entering like this on the walls, there will be water flowing on the wall slowly, call it wall flow, the steam push it on its way slowly. Small droppers of water move spin, spin, and then when it reaches the top, they will split on the wall and fly with the steam. If we can see that effect, that will do it. I don't know what changing from one solve work to the others is all good. Let's stick with one geometry eyeballed. Is there anything you can show me from wherever you are now?
[0:21:03] Speaker 1: I mean, I guess I have the plots and stuff, but we'll send down teams. Yeah, we can send down teams. Sorry, I didn't bring my laptop here. Yeah, I can. So, I bought the geometries, because yeah, we're not too sure about that, and
[0:21:23] Speaker 2: there's a lot of details we are not included. For example, this pipe sticking out, there are some supports holding
[0:21:30] Speaker 1: it. Okay,
[0:21:31] Speaker 2: so it doesn't wobble. We don't want to go there. Yeah, is how do we have inlet conditions that's different from a homogeneous mixture, because it is not a homogeneous mixture.
[0:21:46] Speaker 1: Okay, so our focus is just mainly on the inlet
[0:21:50] Speaker 2: inlet, and see how that affect the steam quality. Okay, we want the steam to be as dry, or if the model show the steam has some droplets of water?
[0:22:03] Andy: Yeah,
[0:22:04] Speaker 2: that's fine, but we then we look at how do we, what do we need to do to stop that or reduce that.
[0:22:15] Speaker 1: I'm going to keep going with, I guess, the pool of water initialized, but if I can't get it to, I guess, stay at the bottom, I guess I will
[0:22:30] Speaker 2: go back to the old one. Yeah, I have no problem.
[0:22:34] Andy: Okay, yeah, okay, yeah. yeah, that sounds good. Yep, yeah,
[0:22:45] Speaker 2: okay. Maybe next time some bring some contours we can look at. Okay, right?
[0:22:53] Speaker 1: Yeah,
[0:22:53] Speaker 2: so we
[0:22:54] Speaker 1: can. I definitely have quite a bit of pictures that I have saved, but still, yeah,
[0:22:58] Speaker 2: CFD, you will always end up with a lot of nice pictures,
[0:23:01] Speaker 1: yeah,
[0:23:01] Speaker 2: just moving through there,
[0:23:03] Andy: yeah,
[0:23:03] Speaker 2: correct, right, yeah, that's fine,
[0:23:11] Speaker 1: and then in when it, and in terms of, I guess, the solver settings, like the mixture, and like the energy, and all the, I guess we're not using energy at the moment, but in terms of all those, we should probably ask my day,
[0:23:23] Speaker 2: yeah, she, she, she'll know the sort of more, yeah,
[0:23:28] Speaker 1: okay,
[0:23:28] Speaker 2: but that energy, you should have energy, because it's the enthalpy is energy,
[0:23:34] Andy: yeah,
[0:23:34] Speaker 2: mass time enthalpy, that's your energy, yeah, so mass two-phase mass times the enthalpy is the energy in the enthalpy of water times mass flow rate water, that's the one component. The other component is mass of steam, enthalpy of steam, that's the those two should be equal to this in steady state, but just the bit we want to see is any droplets of liquid flying with the steam, that's the bit we want to see if it's happening or not happening, and when it's happening, and why these things, so that's the exploration side of things, and if the different solvers give you different answers, we want to see why.
[0:24:29] Speaker 1: Yeah, so we should wait, so we should, so for the, for the, for us to track, like, I guess the particle droplets, we should be like injecting
[0:24:42] Speaker 2: the droplets. These droplets come from the liquid itself, but if you add a tracer in the water, you'll be better able to track those droplets, because they will have. A tracer with
[0:25:04] Speaker 1: didn't go anything to say,
[0:25:10] Andy: yeah. No, I don't know.
[0:25:11] Speaker 2: Well, basically we're not interested in those teeny droplets that fly with this team. I don't know how you see them. They will be small. We just want to see when that's happening. It is happening in real life. It's causing problems, and so what later on, we want to see what we can do to stop that,
[0:25:35] Andy: because
[0:25:35] Speaker 2: that steam go to the turbine and the turbine blades don't like water, they like dry steam, moisture corrode erode turbine blade.
[0:25:47] Andy: Yep,
[0:25:47] Speaker 2: so this is the turbine blade.
[0:25:52] Andy: Yeah,
[0:25:53] Speaker 2: so it sits on the shaft, this part, so this, it looked like, if you look, it looked like a foil when this bit get your audit get cut like this, disappear because of those teeny weeny droplets. So we want to see when this is happening and why, and what can we do to do is slow down the fluid coming in, slow it down, make the thing big.
[0:26:26] Speaker 1: So maybe, maybe we should just go back to the what we, they were doing first.
[0:26:30] Speaker 2: I have no problem with that. I'm not after the water, I'm after the steam. So, yeah, whatever, make life, yeah, yeah, don't complicate life when you really are focusing on one thing,
[0:26:41] Speaker 1: okay, so
[0:26:42] Speaker 2: it's bad enough the way it is,
[0:26:43] Andy: yeah,
[0:26:44] Speaker 1: yeah, okay, I guess we just go back to cutting it and then really focus on the, I guess, the inlet,
[0:26:52] Andy: yeah,
[0:26:53] Speaker 1: and then getting getting to trace the particle, they did the job, but
[0:26:58] Andy: yeah,
[0:26:58] Speaker 1: yeah, okay, okay, that sounds, that sounds a lot more manageable, because I was kind of struggling quite a bit with, I guess, the water pool, yeah,
[0:27:09] Speaker 2: I mean, I've just followed what you said, if you want to do it this way, I have no problem this way, that way,
[0:27:15] Andy: yeah, okay,
[0:27:15] Speaker 2: we are interested in the liquid. We're interested in the steam, like any teeny weeny droplets in the steam. And look at the walls of the separator. How is there any moisture on the walls, liquid fly moving on the walls? Yep.
[0:27:34] Speaker 1: Okay, okay, okay. okay, yeah, that sounds good. I think I can definitely, I definitely have more clearer goal to the thing, though. Yeah, yeah, yeah. Thank you, thank you guys.
```

</details>

