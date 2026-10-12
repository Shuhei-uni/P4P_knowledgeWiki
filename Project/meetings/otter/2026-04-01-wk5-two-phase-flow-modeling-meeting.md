---
otter_id: "acZ2UXe2ZSKVXhbZm-EhZy_1OL0"
source_url: "https://otter.ai/u/acZ2UXe2ZSKVXhbZm-EhZy_1OL0"
source_start_time: "2026/04/01 18:07:05"
source_timezone: unspecified
imported_on: 2026-10-12
---

# Wk5 - Two-Phase Flow Modeling Meeting

| Field | Source value |
| --- | --- |
| Date and time | 2026/04/01 18:07:05 (timezone not supplied by connector) |
| Duration | 16m 4s |
| Source | [Otter recording](https://otter.ai/u/acZ2UXe2ZSKVXhbZm-EhZy_1OL0) |

Imported from Otter.ai. The summary and action items are Otter-generated; they record the meeting and are not verified project results. Original speaker labels and wording are retained. File dates use the timestamp supplied by Otter, without timezone conversion.

## Otter summary

The team discussed modifying a spiral geometry for a two-phase flow model, aiming to achieve optimal efficiency in a cyclone separator. They plan to complete ANSYS learning by April and present initial results by mid-year. The goal is to model different inlet flow regimes to optimize steam output. They emphasized the importance of model calibration and validation, noting that historical data may not apply to modern separator sizes. The team will replicate a 2013 CFD paper to ensure model accuracy. They also discussed the need for a spiral inlet to reduce pressure and improve efficiency, aiming for a 99.9% simulation result.

## Otter action items

- Andy - : Replicate the 2013 CFD paper setup and run the ANSYS model to reproduce results
- Speaker 1 - : Submit the literature review/materials tonight (submit by tonight as stated)
- Speaker 1 - : Update the Gantt chart to add verification and validation (include model calibration and validation tasks)
- Speaker 3 - : Obtain industry data on different separator sizes for comparison (work in progress)

## Full transcript

<details>
<summary>Show the complete speaker-attributed transcript</summary>

```text
[0:00:03] Speaker 1: Know, Like, I said, you can modify the grid,
[0:00:09] Andy: yeah, I think, yeah. I think there's actually the spiral geometry is like, like, it's sketched in there, yes, so it hasn't been extruded. So I think I can just do that.
[0:00:22] Speaker 2: Is, yeah, yeah, sorry. I sent the literature on the weekend, but obviously that was a bit late, so, but I got it done now. I'll submit it tonight, and for the Gantt chart, would you like us to submit it with the report? Yeah, and not in the
[0:00:50] Unknown Speaker(s): report. And then I do, do you want to have a look at a gunshot? Actually? Yeah, oh yeah. It's a bit rough. But I individuals, yeah, but the Gantt chart should be the same. That's what we have in mind.
[0:01:19] Speaker 3: So this April is in May, right? All the months should be, should be here, yeah, yeah, not every two months.
[0:01:27] Unknown Speaker(s): Yeah, sorry, no, I doubt definitely
[0:01:29] Speaker 3: means so you're expecting to do ANSYS learning by first, by May, by end of this month. It shows that answers learning by end of this month,
[0:01:40] Speaker 2: May, yeah, sorry, I completely skipped May. Okay, yeah, it's supposed to be April, and then
[0:01:47] Speaker 3: May, yeah, April. So this one is going to here, yeah. What do you mean? Single model?
[0:01:56] Speaker 2: So just working with the so given the geometries, we just put like in all that stuff and just see,
[0:02:04] Unknown Speaker(s): that's what we're kind of doing right now, yeah, kind of have it, yeah, you're Doing
[0:02:09] Speaker 3: this past model. So from May till June, to around July. Okay, so it means that for you have some initial result about two phase, two phase model for mid year presentation. You know that you have a presentation, yes, it's happening at the first week of August. So here you can just show your simulation result for two phase,
[0:02:47] Speaker 2: okay, yeah, yeah. So I kind of have, like, analyze the results around here, and then kind of like making the reports, or like, the presentation, okay, yeah, great. And then once, I guess the simple, or like the very basic two phases done, then we can work on, like, the, I guess, adding different kind of flow regimes, or, like, trying to add a little bit more complexity and, like realism, I guess, to the to the flow, so it's Not just uniform.
[0:03:20] Andy: Or, yeah, I mean calibration effectively, but I guess, like, in my head, for this part, like, where we're actually improving it is, we're trying to model two phase for the different like, are we going to have different cases? Is that how we're going to do it?
[0:03:39] Speaker 1: No, we want the optimum desire that gave you the best, the best efficiency of separation. And so this is the cyclone that that inlet is everything, yeah.
[0:03:55] Andy: Because what I mean is, like in the paper, you have, like a diagram for different inlet flow regime, yes. So are we gonna try to replicate like each case, like each flow regime at the inlet? Is that like an individual?
[0:04:12] Speaker 2: Should that be like, like they're all combined together, like we have to do
[0:04:17] Unknown Speaker(s): that separately for each run, right? I think. Can you explain again? Um, I can pull it up. It's like a good picture.
[0:04:30] Speaker 1: So here, so no no, sorry, yeah, I see no, not, not for every floor regime, yeah, but we want to get the best angle, the best rotation that give us the cleaner steam outlet with the highest efficiency of the separator, the highest 100% basically. So the inlet condition in two phase flow, you can only have slug, slug or annular flow. These are the ones we have in geothermal these is can exist in the pipe. By the time it arrives at the separator, you expect one of these, right? Okay, yeah, yeah, it's Yeah, so why that? So what we want to get out of this is the best. Because if you want to put this one that your inlet condition should be a wave that change, yeah, the inlet condition you need to provide this way. It's different
[0:05:39] Andy: for us to model these two, right? Yeah, we have to do it kind of have two to inlet condition, like two models, yes,
[0:05:48] Speaker 1: but again, working on the inlet. So the inlet, in this case, you see the inlet is basically square by the time it hit the separator. But originally that used to be a pipe, and it just expand. Transition from a circular cross section to a square cross section, smoothly to give and yeah, some become a rectangle. It enters here and it goes down like the inlet here. Is like this, and then the separators here. So we want to and that's a circle. That's a rectangle. This is a circle. The idea is this. All of these are attempt to maximize sending the water down, then the steam up, and then we can play with the velocity of the inlet. You know, all the calculations you shown that that paper was built around a 30 inch separator, which is three quarters of 75 centimeters. Separators are becoming three meters in diameter. So what the experimental stuff was done in the 50s, not applying to all sizes. So maybe when we go big size, we maybe need to slow down this, change this. So that's, that's the small changes we're going to do to get it, to give you efficient, less water going with this team. But in terms of you can, even if you work with one of these is fine. You procedure,
[0:07:43] Speaker 2: and with the size of the actual things is that, should we just keep on using the geometries that we got given and just change the inlet? Yeah, okay,
[0:07:52] Speaker 1: for now, yes, okay. I'm trying to get some data from the industry to for a different size, different separator, work in progress.
[0:08:07] Speaker 3: Can you back to the gun chart? So, but you know that for after each modeling, you need to verify and validate that, yeah, even by previous literature review, by study or from empirical data or analytical model. Where do you want to do that?
[0:08:33] Unknown Speaker(s): Maybe this goes under this one,
[0:08:36] Speaker 3: yeah, you need to just mention verification, validation as well. Don't forget to do that. Yeah, don't underestimate that.
[0:08:44] Speaker 1: So call it model calibration and validation under here, yeah, that takes the most time when you have something running and going and you want to try this, change this, yeah.
[0:09:10] Speaker 3: So do you have any kind of initial result from your safety?
[0:09:15] Speaker 1: So when you when you run it, what did you get? Did you run it?
[0:09:18] Unknown Speaker(s): I do just, yeah, I did. What did you get contours? I mean, um,
[0:09:28] Speaker 3: do you understand those values? Or this is just a beautiful, colorful stuff, yeah, colorful stuff. It's very important to understand those contours, or those values.
[0:09:41] Speaker 1: I mean, to know efficiency, you can send with the flow particles traces and see where all some of those traces go with the steam and some of them go with the water, you know, trying to assess the efficiency to make sure steam comes out dry, unless, let's drop droplets of water,
[0:10:04] Andy: yeah, yeah, yeah, I managed to get it running, but like nothing. Haven't done anything to actually get results yet. I'm just, yeah, I'm referring to the 2013 CFD paper. So I'm just, I'm just trying to do exactly what it says,
[0:10:24] Unknown Speaker(s): Good, replicate one paper.
[0:10:27] Speaker 2: Yeah. I'm still kind of watching tutorials on how to actually run the answers.
[0:10:36] Unknown Speaker(s): Yeah. So which paper you're going to replicate this one. But this is a Too Faced, but you're working with this simple
[0:11:01] Andy: fluid, yeah, but like, like, because there's, like, like, all the modeler or, like, inlet velocity, trying to replicate things, because the because the geometry is from this paper too, yeah, yeah, we have this one, so I'm just trying to do everything that, that you did for that one.
[0:11:36] Speaker 3: Yeah, yeah. It's a good, good approach to just at the beginning, replicate one of the paper to get to see if you can get the same result and in your company with your model. But again, another thing is that to understand, what does it mean, those vectors, those values, maybe
[0:11:56] Speaker 1: there was changes in the software that was 12 years ago or something. So maybe the software has more features, more features, or the resolution, and you know, the equation it's solving has kind of been modified or fine tuned or something, run all the way, the results are different that something has changed in the software itself.
[0:12:32] Speaker 2: So we'll change the Gan chat a little bit to add the verification and validation, and then I guess we keep working on I get the
[0:12:42] Speaker 3: initial model. Yeah, so next week is a mix and separate. Do you want to have the meeting? Or I'm on leave for two weeks?
[0:12:54] Andy: Yeah, probably not. Then, if you I mean,
[0:12:58] Unknown Speaker(s): I'm around next week, but the following week I'll take leave, I mean, so I'll be here Wednesday, Thursday, Friday, okay, which is, I guess maybe we'll
[0:13:20] Speaker 4: just make it with week seven or week six. Week Six, yeah, okay. Think it's fine for the next two weeks. We just work on this. Okay, yeah,
[0:13:30] Speaker 1: week six. So when you've emailed, he'll get back to you eventually, but what we want to get out of him is the spiral inlet. So make sure you get the files for you have back. Now we want the spiral inlet so you can replicate the spiral and take it further, starting from there on the spiral inlet model, if you look it also has the, if this is, you know, the separator, the inlet here, it's kind of there are in a funnel, yeah, yeah, yeah. The others are straight, yeah. This sort supposed to help reduce pressure at the inlet. However, normally in the separators, there's some layer of condense seeds and then some drops fall and go with the steam. Yeah. Well, we'll find out at a damp coffee, at a down call, some people suggested put it like a Broly an umbrella here, so that steam come and go, but the droplets that on the walls and that umbrella is far away, so it's not affected by cooling From the outside, it is insulated with some thick fiber glass. But nothing is perfect. Yeah,
[0:15:17] Andy: it's kind of crazy that we're trying to improve on like 0.2% Yeah, because it's like 99.98
[0:15:24] Speaker 1: something right in reality, it's no it's wrong. It's over estimated efficiencies. Because in real life, we're not getting that something is not 100%
[0:15:39] Speaker 2: I guess we have to Try to get 99.9% in the simulation first. But yeah,
```

</details>

