---
otter_id: "6j1b3hW67IV1sBSkEN221ga_IBM"
source_url: "https://otter.ai/u/6j1b3hW67IV1sBSkEN221ga_IBM"
source_start_time: "2026/09/21 14:58:47"
source_timezone: unspecified
imported_on: 2026-10-12
---

# Separator Simulation Progress Update

| Field | Source value |
| --- | --- |
| Date and time | 2026/09/21 14:58:47 (timezone not supplied by connector) |
| Duration | 21m 13s |
| Source | [Otter recording](https://otter.ai/u/6j1b3hW67IV1sBSkEN221ga_IBM) |

Imported from Otter.ai. The summary and action items are Otter-generated; they record the meeting and are not verified project results. Original speaker labels and wording are retained. File dates use the timestamp supplied by Otter, without timezone conversion.

## Otter summary

The team discussed progress in managing liquid behavior within the separator simulation to reduce liquid carryover into the steam outlet.

### Simulation Progress
**Shuhei** reported improvements in driving liquid lower in the container by increasing iterations to 4,000–5,000, which helped reach a steady state. Previously, high momentum caused liquid to spiral upward, resulting in 200 kg/s of liquid entering the steam outlet; current results show this has decreased to 22 kg/s. To address remaining issues, **Shuhei** is testing a small pressure outlet ring at the bottom to mimic an absorber and control pressure more effectively. **Andy** is performing similar tests using full geometry rather than a cutoff geometry to see if extra room at the bottom assists liquid removal. However, **Andy** noted that increasing the size of the removal region does not necessarily increase the amount of liquid removed and mentioned numerical instability where one case blew up after 4,000 iterations.

### Technical Challenges
**Liquid Control Strategies**
*   **Shuhei** is experimenting with ramping up inlet velocity more gradually to allow gravity more influence over momentum.
*   **Sadiq** suggested adding physical geometries like ramps or steel angles on the walls within the mesh to force downward flow and block upward momentum.
*   The team remains uncertain if these mechanical interventions will successfully drive down the thin film of moisture on the walls or if they will merely introduce new complexities.

**Project Constraints**
*   Can a mechanism be designed that allows for artificial pressure control and liquid removal without allowing steam to escape through the bottom ring?
*   Will implementing wall-mounted features significantly improve convergence or just provide exploratory findings for future implementation?

The final report is due in mid-October, following Systems Week. The team aims to complete experimental work this week and prepare a draft poster by October 12th for review during the next meeting.

## Otter action items

- Shuhei - : Continue testing the thin pressure-outlet ring by correcting the bottom absorber setup and artificially blocking steam flow while retaining liquid removal and pressure control.
- Andy - : Modify the liquid-removal function to remove liquid more gradually and evaluate whether this improves numerical stability and convergence.
- Shuhei - : Test an exploratory wall-mounted ramp or insert near the inlet to redirect accumulated liquid downward and assess whether it reduces the liquid layer on the wall.
- Shuhei - : Continue using a slowly ramped inlet velocity to reduce excessive momentum and improve downward liquid flow.
- Shuhei - : Prepare and send the draft poster for review by October 12.

## Full transcript

<details>
<summary>Show the complete speaker-attributed transcript</summary>

```text
[0:00:17] Shuhei: So I didn't record anything the last week.
[0:00:21] Speaker 1: That's okay.
[0:00:26] Andy: Hello. Hi, my dear. Good. Okay. Yeah.
[0:00:37] Shuhei: Okay. So I guess I'll just pick up from where we left off last week. So last week we were mainly, I guess, struggling. So we were mainly struggling on the liquid being liquid was going into the temperature. Yeah, in the container. Yeah, yeah. But so liquid was going above the. It was going in, but it was staying above the inlet, and it wasn't really going down, where I was had the absorber, the the function that removes the liquid. So even though the function was there, like because the liquid wasn't going lower, it wasn't actually getting removed. So I was trying to, I guess, solve that so we can drive the liquid lower and then actually actually close the continuity continuity field, so that was the plan, and actually I did see some improvements.
[0:01:27] Speaker 2: You wanted to increase the iteration, I guess I can. Oh
[0:01:30] Shuhei: yeah, I also did a lot more iterations. So previously, I think I was only showing you around like 1500 iteration, but I ran a couple other ones to like 10,000 iterations, and what I found out was most it kind of became steady after around 4000 to 5000 iterations. So most of the all the cases that I run now are at least around to 4000 iterations because that's where I found to be steady kind of starts. So once that kind of starts, I've just paused it and then just got the results. So yeah, so this is, for example, this one is to 4000 iterations. So that's when I started seeing the steady, like state come in. So previously last, I'll show you my last. One second
[0:02:34] Speaker 3: get the volume fraction, and
[0:02:41] Shuhei: so we can. There's too many triggers for me to actually. Yes, this technically not right. I definitely had a contour. I guess this works. So I guess this one. So if you look at this one, so this is what was happening last time, and I wanted to resolve. So a lot of the liquid was. So this is where the inlet is, and a lot of the liquid is essentially above the inlet, right? So once it enters, it just kind of spirals up and kind of pull it. And also, there's a, I think there's too much liquid on the wall. There should be a lot less. It should be a thinner film. And then, so I was able to kind of, I guess, improve it. So this is a lot less liquid. Correctly, but so this is a lot less liquid on the wall. The scale
[0:03:51] Sadiq: is sorry. The liquid on the wall is correct.
[0:03:54] Andy: Yeah, yeah.
[0:03:55] Sadiq: If it's a thin layer, that's fine.
[0:03:57] Shuhei: Yeah, yeah. But it was as I do more iterations, it just like ballooned up, and it should be it should be like a film on the wall. Yes. But it shouldn't be like a pool of liquid on the wall. Most of the
[0:04:09] Sadiq: liquid is going down, right?
[0:04:11] Shuhei: Yeah. So that was the previous issue. I wasn't able to get the liquid to go down, right? So that was the kind of the goal here. And although it's most liquid is kind of around the mid area, where just above the inlet, but I was able to drive the liquid a lot more further down, and now this doesn't actually tell you the story, but I did see quite a bit of improvement in continuity, lowering, so that's kind of I guess where I'm at. I guess so. Previously, I'd see. I don't have the actual data over here, but well, I do. But it's gonna be quite a bit to figure out. So previously, I had like because there was so much liquid in Separator itself, there was like 200 kilograms a second of liquid going into the steam outlet, which is obviously not completely not the behavior that I want, right? But with the absorber, the I was able to because I was able to drive the liquid more down. I was I got that like 200 kilometers per second to down to 22 right now. So it's still a lot, but it's it's a significant improvement to the previous the amount of liquid going into the steam outlet, so yeah, that's where I'm at. But I'm hoping, and I also so I'm so that's kind of the improvement that I saw. But obviously, the continuity field is still not closing, or the continuity is not closing, and I need to drive more, I guess, liquid lower, and somehow not get liquid to kind of spiral up and just like pull at the top. Well, that's it for you. What when it's pulled? What does it happen? Does it go with the steam? Yeah, it just pulls and then so essentially what happened previously was it'll pull up at the top area and then like a lot of it will go into the steam outlet. So that's why the steam outlet had like 200 kilograms a second of liquid going in, which is completely not what I want to be happening. Yeah, and also I think I talked about this last time a little bit, but getting like a like a tiny pressure outlet ring at the bottom. Yeah, yeah, yeah. So the the case that I was working on there, the absorber, I didn't actually configure the absorber correctly, so I don't actually have the result to show it. But I, from I just quickly had a look at the result of the simulation just like 20 minutes ago. It showed decent behavior in terms of the the pressure and how liquid it was essentially on the on the wall. So with the with the with I'll fix the absorb how the absorber will work at the bottom. So absorber meaning like this bit of so if liquid goes into this bottom part part, it'll just get removed. So I'll fix that now. So if I fix it and use this pressure outlet, I think I can artificially control the pressure a little bit better, but also I did see steam going out of the tiny ring that I created, so I might have to like somehow come up with like an artificial way to like block the steam.
[0:07:37] Sadiq: Yeah,
[0:07:38] Shuhei: but allows allow the pressure control and still allow for liquid removal as well. So just kind of trying to artificially like mimic the behavior of the.
[0:07:48] Sadiq: So normally, if this is the inlet here, this is up to here is all full of water still.
[0:07:55] Shuhei: Oh, is it to like here?
[0:07:56] Sadiq: Yeah, no, up to here. Okay, yeah,
[0:08:00] Shuhei: yeah. Yeah. Yeah. So I I kind of see hope with the the pressure outlet ring that I was working on. So because I I made some mistakes on setting up that case, I wasn't able to get like actual clear result that I could kind of report on. But I think there is some possibility of actually that could be working, so I'm gonna keep trying that a little bit more, and then maybe we might be able to add something to the final report based on that. But at least what I'm happy with is that we were able to like get the liquid to at least decrease from crazy high number to obviously 22 kilograms per second from steam outlet is still massive still, but it's it's at least a good in a in a good direction, so yeah, that's where I'm kind of yeah.
[0:08:52] Speaker 2: So you are working at the same.
[0:08:54] Andy: We're sort of trying the same thing. We're doing something similar. I'm basically doing what he's doing, but I'm trying it with the, cause he's trying it with the cutoff geometry. Yeah. I'm trying it with the full geometry. Um. So essentially. So in Shu Hayes one, it only goes up to there, like it. It's only modeled up to that that part. Yeah. Um. For me, I'm. I'm basically doing the same thing, but with the full thing, because again, the the the problem was like not enough of the liquid was going down. So I thought maybe if there's an extra, there's some extra room down there, maybe it would go down more. So I just tried it for like five different cases, like how large the removal region is, up to where the water line was assumed to be. Results didn't didn't work like 100% What was really interesting was actually, as this increase, it doesn't necessarily mean that more liquid was removed, which is really interesting to me.
[0:10:22] Sadiq: So can you go back to that geometry? So this this is where the pipe is coming out, right? Yes. The steam pipe.
[0:10:30] Speaker 4: Yeah.
[0:10:31] Sadiq: So you're taking somewhere from here, or all of it
[0:10:35] Andy: is? So it's I tried five different
[0:10:39] Sadiq: outlets,
[0:10:40] Andy: like five different cases where, like five different levels, so inside
[0:10:47] Sadiq: of water inside,
[0:10:49] Andy: of where the water would be removed. So this dotted line here is where we assume the water level would be. So I guess what we're trying
[0:11:00] Shuhei: to mimic is if the liquid goes into the place, then if there was a pool, it's essentially kind of just turning into nothing. Essentially, that's what I'm kind of imagining. So that's yeah,
[0:11:12] Andy: yeah, yeah. But yeah, the fact that as this increase, the amount of liquid that's removed doesn't increase, doesn't necessarily increase with it. is It's kind of interesting. Honestly, I'm not entirely sure why that's the case.
[0:11:37] Shuhei: Yeah. Wonder if we have enough time to actually. I feel like we are moving like a little bit by a little bit onto the right direction, so they're hopeful. But also we are running out of time crazy.
[0:11:53] Andy: Maybe because for the for the final case, for the one where it was the the the removal region, the level was the largest. It actually blew up after like 4000 iterations. So this is like the residuals. So maybe I'm guessing could perhaps to do with like the the the fact that not more liquid was removed necessarily could be something to do with the like numerical instability maybe
[0:12:34] Sadiq: without residual yeah
[0:12:36] Andy: yeah but um I mean that's for the last case. Like it completely blew up after 4000. But this is for the other cases. I mean the residuals look like similar, similar, similarly bad. I guess. Ah. So next up for me, I'm gonna try to do the function with, like, um, for the removal function, make it remove liquid maybe more gradually. See if that helps. Does that sound right to you? For the for the
[0:13:23] Shuhei: liquid removal, I'm just kind of like matching the the inlet flux. Like whatever's inlet is whatever how much I try to remove at the bottom. So that's how I kind of try find the steady state. So whatever's going and should end up hopefully at the bottom, then gets removed. It should be the inlet should be removed at the same time, like same rate. Yeah, that's kind of what I'm going off of. But
[0:13:52] Andy: okay,
[0:13:53] Speaker 2: I think you already modeled the full geometry just a couple of weeks ago. Oh yeah, yeah, no, I found that it's you you won't get the convergence. That's why you cut.
[0:14:03] Shuhei: Yeah, that's what I did. But and that's why
[0:14:06] Speaker 2: I'm just a little bit. Oh, so you're going to model the full one, although you know that you didn't get the convergence.
[0:14:13] Andy: Because for that one, we were trying to model the the liquid pool like explicitly. Yeah.
[0:14:19] Shuhei: Yeah, I was focusing more on the grion outlet control, whereas he's focusing more. Because
[0:14:25] Andy: for for this one, even though I'm doing the full geometry, I'm not modeling that as a pool, as like liquid, like a liquid pool in there. That's that there's just to show you where the the function to remove the liquid is so it wasn't that the full geometry is the problem. Is that we had the full geometry and then we had the brine outlet and then we weren't able to like figure that out with the liquid pool and how that was gonna go out of the brine outlet and then the steam was gonna come up. So that was the issue there. Like the full geometry isn't the the the issue.
[0:15:05] Shuhei: I guess one more weekend though, if we can't move
[0:15:14] Speaker 2: this. So one more
[0:15:16] Shuhei: week. One more week to try really like push for the more experiments. Yeah.
[0:15:20] Speaker 2: So the report is around mid of October next week. Isn't Systems Week? Systems Week. There is no meeting. Oh yeah. Yeah. So you should focus on. Yeah. Yeah. Systems Week. Yeah. So you will have another two weeks, yeah.
[0:15:43] Andy: Yeah. Okay.
[0:15:44] Sadiq: So those last two weeks is for writing and tidying up. Yeah. So for the experiments,
[0:15:50] Shuhei: mostly like this
[0:15:52] Sadiq: this week.
[0:15:54] Shuhei: Yeah. I mean, obviously, we'll be able to steadily still keep. Yeah. I mean,
[0:15:59] Sadiq: in reality, this is as far as you guys managed to get, and that's not a detriment to your work. It's just that it shows the challenge, and someone else needs to come and take over, and eventually, and so. Yeah,
[0:16:17] Shuhei: I mean, I feel like we made enough mistakes for the next person to be like, okay, that's not. I'm not doing this or this. That's still problems. Okay. Well, I would try work on the thin pressure outlet ring, and then try kind of artificially block the steam from actually coming out, but still being able to artificially control the pressure at the bottom, so we can try and mimic the behavior of the middle separator. We'll see where that takes us, but yeah, that's
[0:16:49] Speaker 2: for the next meeting, which would be two weeks. Oh yes, if you can send us the poster because the deadline of the poster is 12 of October. Yeah, that's the draft of the poster. Then we can discuss about on the meeting. Okay. Yeah. Yeah. Okay.
[0:17:05] Shuhei: Yeah, that sounds good.
[0:17:08] Sadiq: To that water going up on the wall. Yeah. That's a layer or big layer. Yeah. Can you put something to bring it down? So I know the walls are smooth, right?
[0:17:21] Andy: Yep. If
[0:17:23] Sadiq: you if you weld something that put something on the wall, just something fixed, push it down. Okay. Because it it is going like this, right? It's piling up like this, and then stay there, and some of it will go enter. Yeah. If you at the inlet here as it enters here and starts spinning somewhere here, you put something that does this. So this kind of just like
[0:17:51] Shuhei: blocks the momentum, so you like gets the
[0:17:53] Sadiq: yeah something on the wall, hit it and come back. Like if I mean if this is your wall, you weld something, and the stuff is the fluid is coming this way,
[0:18:06] Shuhei: kind of like a ramp to it.
[0:18:08] Sadiq: Yeah, something that brings it something like this, but it's yeah tailored, shaped like this. So, like you want the piece of steel angle, that water comes and hit, and wants to go, but it hits, captured here, and this is pointing down. So that water is forced down.
[0:18:31] Shuhei: We could definitely do something like that, but I'm not too sure how that would, because we haven't really got an actual real, I guess like a mimicking separator. If we do that, then we might. I mean, we could work up with something like that because it's not that difficult to just add that into the mesh. Yeah.
[0:18:54] Sadiq: See, see if if if you can just to show that. Okay, we're still having got the balance right, and we're still getting too much. If we put something like this, even if the match is not perfect, can this drive that layer of moisture down? I know we haven't got the right steady state, but if this shows an improvement,
[0:19:17] Shuhei: then I guess that's a finding that we can talk about.
[0:19:19] Sadiq: Talk about to future implementation.
[0:19:23] Shuhei: Okay. So just as like an exploratory thing, possible. Yes. Yeah.
[0:19:27] Sadiq: And that's kind of a possible solution, but we still haven't got that thing converging 100%
[0:19:33] Shuhei: Okay. Yeah. I mean, we can definitely do something like that. So water
[0:19:35] Sadiq: get come here, but this this thing is pushes that water down.
[0:19:42] Andy: Yeah,
[0:19:43] Sadiq: it's not a. It's not. Yeah, or you can just put it straight. It's
[0:19:46] Shuhei: more like a spiral going like down. Is what I'm imagining.
[0:19:49] Sadiq: Yeah, or or just put something like this and go vertical.
[0:19:53] Andy: Okay. Yeah, yeah. Because so it just comes
[0:19:55] Sadiq: here, hits that, and the water goes down. So you reduce some of the water that's there.
[0:20:02] Shuhei: Yeah, actually, that reminded me of one thing that I forgot to talk about. the The main component is, I guess, the inlet velocity is super. I'm kind of going at full speed at from the start, so I thought that was kind of the problem. Why, because there was so much momentum, it just kind of got the liquid to just stay up, and because it's so, you know, it has so much momentum, it doesn't really get the gravity to act enough to drive the liquid down. So I kind of started with really slow inlet speed, so it kind of like slow has more effect. The gravity affects it more to I don't know kind of try create the field slowly, so it's not just pure momentum just driving it up. So I think that also is one of the key things that improved the liquid from pulling higher. I can't say for sure that was the entire reason, but I think that did help a little bit. So I will keep working on with like the slow ramped increase in inlet speed or inlet plots. Yeah. Yeah, yeah. Let's go now. Yeah. Okay. So we'll get the poster ready for the next time, or the draft poster. Yeah. Yeah. Okay. Yeah. Sounds good. Thank you. Thank you.
```

</details>

