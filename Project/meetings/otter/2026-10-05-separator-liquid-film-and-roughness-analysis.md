---
otter_id: "hglR96KhH_0P4HfOlEVOn03oJJk"
source_url: "https://otter.ai/u/hglR96KhH_0P4HfOlEVOn03oJJk"
source_start_time: "2026/10/05 14:01:58"
source_timezone: unspecified
imported_on: 2026-10-12
---

# Separator Liquid Film and Roughness Analysis

| Field | Source value |
| --- | --- |
| Date and time | 2026/10/05 14:01:58 (timezone not supplied by connector) |
| Duration | 28m 42s |
| Source | [Otter recording](https://otter.ai/u/hglR96KhH_0P4HfOlEVOn03oJJk) |

Imported from Otter.ai. The summary and action items are Otter-generated; they record the meeting and are not verified project results. Original speaker labels and wording are retained. File dates use the timestamp supplied by Otter, without timezone conversion.

**Source discrepancy:** The summary compares 0.008 m with 0.0456 mm and calls the former lower. The unit comparison is reversed: 0.008 m = 8 mm. The original wording is retained below.

## Otter summary

Shuhei and Sadiq discussed the progress of liquid behavior modeling in a separator using **Fluent** to improve simulation accuracy.

### Simulation Modeling
**Shuhei** explained the methodology for developing a stable field by using slow inlet loading, increasing velocity from 28 m/s to a maximum of 116 kg/s. This approach is necessary because highly turbulent models can behave poorly if full speed is applied immediately. **Shuhei** also highlighted the use of the **Eulerian wall film** model in **Fluent**, which allows for simulating interaction between liquid and walls through friction and shear forces. This modification significantly reduced the liquid escaping through the steam outlet compared to simulations without wall film enabled.

**Wall Film Dynamics**
The development of the wall film is a transient process that requires significant computational time; one simulation required 45,000 iterations to reach development stages. Current findings show approximately 6 kg of liquid sitting on the wall, though it has not yet reached a steady state and may require more iterations to stabilize. A primary concern remains whether performing mesh conversions on such fine meshes will be feasible within the two-week deadline for the report.

### Design Iterations
**Shuhei** presented two design iterations involving physical changes to the separator to reduce liquid carryover: a structure designed to block liquid from being carried by inlet steam and an angled version intended to redirect flow before reentrainment occurs. While these results were still being processed, **Sadiq** noted that prioritizing a well-written report over high-risk modeling tasks is essential given the upcoming deadline.

**Roughness Optimization**
Following feedback regarding roughness values, **Shuhei** intends to rerun simulations using more realistic parameters based on a **Moody chart**. Currently, the modeled roughness (around 0.008 meters) is significantly lower than commercial steel (0.0456 millimeters). The team discussed how increasing roughness could further decrease momentum at the wall and reduce liquid escape at the steam outlet.

**Future Considerations**
The meeting concluded with potential ideas for future research, such as adding external collection pipes or cuts on the shell to capture accumulated moisture without altering internal wall roughness. Could adding a specialized collection mechanism effectively prevent particle jumping?

## Otter action items

- Shuhei - : Run simulations for both proposed separator bar designs and obtain results for the poster, preferably by the end of today.
- Shuhei - : Contact Mida/Manda for feedback on the reduced continuity value.
- Shuhei - : Rerun the separator simulation using the corrected commercial-steel wall roughness value and assess its effect on liquid carryover.
- Shuhei - : Prepare a draft report by next week and finalize it with the modeling results and systematic methodology captured before the report deadline in two weeks.
- Sadiq - : Send Shuhei the Moody chart for relating wall roughness to friction.
- Shuhei - : Document an external liquid-collection pipe or drainage path as a future separator design improvement to prevent upward liquid carryover.

## Full transcript

<details>
<summary>Show the complete speaker-attributed transcript</summary>

```text
[0:00:03] Shuhei: Potentially used to be like the entire liquid, which is like yeah yeah. So yeah, it's still definitely not perfect, but it's gotten much better. At least there's there's a path for liquid to escape now. So
[0:00:22] Sadiq: now, what's the difference between A and B?
[0:00:24] Shuhei: So, so the initial start, the 1000 like the yeah to that is essentially just really low inlet speed. So just developing, just trying to develop a stable field with really low inlet speed,
[0:00:38] Sadiq: and you add more. And
[0:00:40] Shuhei: then the A is essentially just like increasing. So I think you can see the liquid increasing. So this
[0:00:47] Sadiq: is the free G. Yeah. So you can
[0:00:51] Shuhei: yeah. So you can see that increasing. You can also see the plot right underneath. So that's just like how I increase it. So it was at like around 28 meters per second, or the velocity of the inlet, and then I just increase it to the max, which is around 116 that I'm using.
[0:01:08] Sadiq: 116 watt
[0:01:09] Shuhei: kilogram per second.
[0:01:10] Sadiq: Yeah, velocity.
[0:01:13] Shuhei: Velocity is like 26 point something. I don't remember off my heart, but yeah, and then I just hold it there. So once it gets there, and then yeah. So essentially, I take it to the max with the inlet, slowly increasing the field or developing the field. So, and
[0:01:37] Sadiq: then, so although it's kind of steady state. You you run it as a a bit of transient just to arrive at. It's
[0:01:46] Shuhei: because the the thing is so turbulent. If I start from this like full speed, it
[0:01:52] Sadiq: will go crazy.
[0:01:53] Shuhei: It yeah it doesn't tend to behave very well. Whereas if I start from yeah if I tend to do slow inlet loading, yeah, it does well, and that's what Fluent advises as well for really turbulent models. They advise you to develop the field really with a slow, less turbulent, violent system, and then develop
[0:02:17] Sadiq: it slowly to the
[0:02:18] Shuhei: max. Yeah. And then I guess this is the second figure. How can I describe this one? So this is essentially focusing more on the Eulerian wall
[0:02:32] Sadiq: film.
[0:02:33] Shuhei: Yeah. So wall film, I knew that was like a significant part of it as well because I think in the previous meetings I've discussed about how there was too much momentum, and with thin layer going in, like the liquid would just like spiral up because it has so much momentum, and it would go into the steam outlet. So it there wasn't a proper model for the interaction between the wall and the liquid. Yeah, so a layout. this wall film settings within the fluent actually enables you to actually model model the the interaction between the wall and liquid properly. So there's like there's going to be friction, there's going to be all those things, and you can get like liquid accumulating on the wall, with without the settings on, you it's it's more of like a it doesn't I don't exactly know the difference, but it's it's not more it's not a more accurate representation, like it's it's not like simulating the interaction as accurately as where you'd enable a wall film with influent, so essentially you can just see. So I think the third plot is the most interesting one. I guess you can just see. So I enabled it, and then you can see the inventory of the liquid film increasing, and then just kind of get reaching to a steady state, and then I think maybe fourth plot is also interesting. So this is essentially just talking. So the the plot above the third plot is talking showing the inventory, whereas the fourth plot is talking about the rate. So how much? Oh wait, sorry. Could you go just a little bit more? Just go back to the yeah this one. So this fourth plot is talking about the rate, and this one is talking about like the total liquid that's on
[0:04:41] Sadiq: the wall.
[0:04:44] Shuhei: Yeah, essentially you can just yeah.
[0:04:47] Sadiq: But six kgs is all sitting on the wall.
[0:04:50] Shuhei: Yeah, yeah, yeah. So that's like the total that's on the wall. Yeah, and then the fourth one, this one is the rate. So it's essentially blue line is essentially showing how much liquid is being added, so obviously liquid goes in from the inlet and then it'll splash onto the wall, so it gets added onto the liquid film,
[0:05:09] Sadiq: and then
[0:05:09] Shuhei: the orange, the brown orange line talks about the drain. So obviously stuff it gets added, but some goes down and then it gets kind of drained in the absorber,
[0:05:23] Sadiq: and that the difference between here and here
[0:05:26] Shuhei: is this. Yes, yeah, yeah. So,
[0:05:33] Sadiq: so there is six kgs at any point.
[0:05:37] Shuhei: Yeah, it's technically not stable yet. It's still kind of slowly, slowly increasing, but yeah, it's it's around six kgs on the on the wall.
[0:05:51] Sadiq: Will that mean that six kgs keep moving up and jump with the water at the inlet, right?
[0:05:58] Shuhei: Um, I think it's just because obviously the drainage isn't immediate because it splashes onto the wall. It'll stay on the wall for a little bit, and then it'll slowly go down and then gets drained. So I'm not 100% sure, but solving for the wall film takes insane amount of iterations, like steps, because obvious this the model we're solving is obviously steady state, but wall film is actually solved differently and it's a transient model. It's solved transiently, so it's actually like iteration, and yeah, time step actually matters. So for example, this one is ran into like 45,000 iterations, with essentially nothing in the simulation changed from like 15,000 iterations, so from E to the end, it was just purely the wall film development. So yeah, wall film development really takes a lot of time. So I I'm not too sure how we're gonna do like measure conversions with wool film because it's gonna take a whole lot of time.
[0:07:05] Sadiq: So you need to have a very fine mesh mesh around the walls to model that they are better than.
[0:07:12] Shuhei: Yeah, it definitely it definitely I think it's definitely a very important part of understanding I think the separator because it's obviously like the main component, like how the liquid behaves and how that reentrants into the steam. So yeah, and then if you look down, I guess we can kind of see. So yeah, that one. That's just like a sensitivity analysis I did based on how the roughness of the wall affects the liquid carryover.
[0:07:42] Sadiq: What is K here?
[0:07:44] Shuhei: So K is essentially like how rough it is. So if you look at like, if it says point 001, that's point 001 meters of roughness. So what? That's a millimeter.
[0:07:56] Sadiq: Call roughness high.
[0:07:58] Shuhei: Yeah, yeah, roughness high. Steel is
[0:08:00] Sadiq: all 0.046 millimeters for commercial steel. Okay,
[0:08:06] Shuhei: I think did I do that? No, I only did two millimeters at max. Okay.
[0:08:12] Sadiq: So you know when you calculate pressure drop on pipes and so on, there's roughness of the walls of pipe. Commercial steel, which is the same material here is 0.0456 or five millimeters.
[0:08:27] Shuhei: In that case, I think K is this one. I think so light blue. So it's around. So yeah. What I'm trying to get with this plot is just how the increase in number
[0:08:39] Sadiq: 00. this a meter?
[0:08:42] Shuhei: Yes.
[0:08:43] Sadiq: Oh, there's another 00. is this millimeters?
[0:08:46] Speaker 1: Oh
[0:08:46] Shuhei: shoot, that's very rough. Okay,
[0:08:49] Sadiq: I will. So
[0:08:50] Shuhei: I haven't done. It's more
[0:08:51] Sadiq: like it's more like this.
[0:08:53] Shuhei: Oh
[0:08:54] Sadiq: yeah, nebultic. What is CS?
[0:08:58] Shuhei: CS is like apparently it's a roughness constant. I'm not. I wasn't fully aware of what it does, but I did do a quick sensitivity analysis on how the constant, how that, how changing that affects the response. I can quickly show you that actually. So this is just. like a sensitivity analysis I did on so how changing C is at at at this roughness. So I need to I need to investigate on what actually C is, but essentially changing C, making C higher does remove more liquid from the steam out there. What does
[0:09:44] Sadiq: it refer to? I mean, physically, sorry. How does it sit in the governing equation?
[0:09:50] Shuhei: So it's it's just how the liquid interacts with the wall. So I can definitely look into this more. I was just doing sensitivity analysis in terms of how the wall, like, because there's there were two main wall parameters. So the how how rough it is, the roughness height, and then this constant C. Yeah, so I can definitely look into it. I know I'm not actually too sure what the C does, but just the sensitivity analysis in how changing C affects the steam outlet being at liquid going into the steam outlet. If you look at the plot below, so this is this is enabling the wall film and how that changes. Obviously, I've talked about it earlier, but this is how. So, if you look at this orange line, that's kind of the baseline. So, essentially, no. That's with no wall film. So, and then if you look at the lift scale, so with no wall film, the liquid escapes about I don't know 2025 kilogram per second from steam outlet.
[0:11:05] Sadiq: That's a lot.
[0:11:06] Shuhei: Yeah, that's a lot. And then when you enable the wall film, you can see the red line going up. So that is reduction in the liquid going out of the steam outlet. So
[0:11:17] Sadiq: making the walls rougher is better.
[0:11:19] Shuhei: No. Okay. So in this case, there's no roughness. It's just actually simulating the wall to liquid interaction. So previously, that wasn't explicitly modeled. It was just the wall and liquid flowing through within the capsule. But with this enabling the wall film, we're actually calculating the interaction between there's a wall and there's liquid, so obviously there's going to be friction and all these shear forces and things, so that's being modeled. So when you actually model that, the liquid going out of the steam outlet reduces significantly. So I think this, like this, is technically my assumption. So you can't, I can't say this, I can't claim this for 100% But I think with roughness and enabling wall film, they're both essentially adding friction to the liquid that's traveling at the wall, so essentially lowering the momentum and therefore getting gravity to act on it a little bit more, thus driving the liquid to lower region more, and that's why the steam outlet is the liquid going out from steam outlet is is reducing. If you increase the roughness, that reduce that reduces the liquid going out of the steam outlet, and if you enable the wall film simulation, that also reduces the momentum. Therefore, the liquid going out of the steam outlet also reduces. That's currently my assumption. Yeah. So essentially, previously, I think like the momentum. There was no way for the liquid to like the momentum would just keep keep building up, with actually enabling roughness and the wall film that actually models the interaction. It slows it down, and actually, yeah. So it's a little bit. I think. I think it's a right path forward to trying to model the more more accurate separator. Yeah, that's where I'm currently with that one. But I wasn't too happy with the first. If you could go up to the very first plugin, I wasn't very happy with that one. So as you can see, you can still kind of see like a spike up at from the first transition to eight.
[0:13:33] Sadiq: Yeah.
[0:13:35] Shuhei: So if you could scroll down,
[0:13:39] Sadiq: which video do you want?
[0:13:40] Shuhei: Just go lower to the one that we haven't seen yet. Oh wait, actually, what was this one? Maybe one lower. Yes, this one. So this one's a lot more zoomed up, so I can't say. But essentially, this is I'm taking the same approach. So, essentially, we do the slow load inlet loading. So we just yeah
[0:14:10] Sadiq: alterations yeah yeah
[0:14:12] Shuhei: and then I
[0:14:13] Sadiq: increase
[0:14:14] Shuhei: increase, and then in this time previously the with the very first port it was it essentially jumped to like
[0:14:21] Speaker 2: here, yeah.
[0:14:22] Shuhei: With but with this one, although it did spike up a little bit here, it quickly went down pretty quickly. So, I was with this. I was just trying to recreate the the first case, but with less iterations because that was like 45,000 iterations, and I'm using a very coarse mesh, so it 45,000 iterations a lot. But because it's coarse mesh, I can still iterate quickly. Whereas if I'm doing like a mesh, well, I'll have to do a mesh conversions later on. Doing 45,000 iteration on a very fine mesh is going to take forever. So I was just trying to recreate the same behavior as quickly as you can. So this is around 5000 iterations. With so you know getting getting closer to the first case, but yeah. And then actually, if you could, I think there was a table on the oh maybe not okay uh wait if you could go down to the very last part so that's also like another visualization on I guess the film developing war film yeah and it kind of just shows how much iteration we need to take. So the very first, like the dark with no film, well, barely any film, is at 5000 iterations, whereas the very end is at 25,000. So just to get from there to there takes 20,000 iterations. Yeah. So and yeah, the final film mass is around 6.6, but it's still developing. So I probably need to run it to like 40,000 iterations. Yeah, just to see if the war film can reach a steady state.
[0:16:16] Sadiq: That number stabilizes.
[0:16:18] Shuhei: Yeah, I need I need to get that number to stabilize. But also, when it does stabilize, and when I when I want to validate that result, I'd have to do mesh conversions, and that would take forever. So I'm not too sure I'm going to do that yet.
[0:16:35] Sadiq: Let's let's look at. I mean, the poster is fine, and it's yeah. When is the report
[0:16:43] Shuhei: due? Like two weeks.
[0:16:45] Sadiq: Two weeks. So not much time.
[0:16:47] Shuhei: But if you could, okay. So could you? Sorry, could you please look at the poster again? So I remember you asking us to come up with like a like a design, like a physical change on the separator to Talk about improving
[0:17:04] Sadiq: that piece of yeah yeah. So
[0:17:06] Shuhei: it might not be exactly what you were imagining. If you look at the right corner,
[0:17:10] Sadiq: yeah, this one.
[0:17:11] Shuhei: Yeah, if you could really zoom in, maybe you can just make it really big. Yeah, just Yeah. So I made two. So this one is like a. It's kind of close off. Can I quickly draw on something? So it's essentially like a. So I guess here's the separator and here's the inlet grunt. So if you have a top-down view, it's essentially just like a like a thing blocking here. So essentially, if the liquid goes in, I'm trying to block it from going carried in by the steam going in. I'm not sure if that's the right intuition, but that's currently the first iteration of design that I made, but you could definitely if you if you have such a version. I mean, this
[0:18:06] Sadiq: is good. This is also it comes like this and like this and that. Yeah,
[0:18:12] Shuhei: that's the idea. Yeah,
[0:18:13] Sadiq: yeah.
[0:18:14] Shuhei: I had ah I I haven't I I've run the first version of it. I haven't been able to get the results here because yeah, that only finished running this morning. But I think I think we can try get the results for those both of these changes by before we finish the poster. So hopefully we have like a proper results on how these physical changes led to the change in behavior with the steam outlet, or something like that.
[0:18:47] Sadiq: Okay. Yeah.
[0:18:49] Shuhei: Yeah. That's kind of over. Yeah, I kind of want to get Mida's opinion on continuity because the continuity is gotten quite a bit lower, which I I think I briefly talked about on the report on the PDF, but yeah, it's still it's still not that low, so I just yeah I kind of I will try I guess reach out to Manda to see what she thinks.
[0:19:20] Speaker 3: Okay,
[0:19:21] Shuhei: Yeah.
[0:19:24] Speaker 4: Yeah.
[0:19:25] Sadiq: What is this right here?
[0:19:28] Shuhei: Oh, so that's just a huge amount of liquid that's pulled up. Because then
[0:19:34] Sadiq: pulling the the bar might be beneficial.
[0:19:39] Shuhei: Yeah, maybe actually. I wasn't looking at that when I was making it. So yeah, it might be beneficial
[0:19:44] Sadiq: because that goes in and then splits and go back. Yeah. So if you if you drop most of it, you reduce that.
[0:19:51] Shuhei: Yeah. Yeah. That's why I made the even for the angled one. I tried to make it before the before the liquid goes into the gets carried by the inlet steam again, so try and reduce the liquid being carried at the inlet again when it goes around. Yeah, that's kind of the idea I had for those two, but we'll see if it actually makes any difference. Yeah,
[0:20:23] Sadiq: I mean, there's limit to what can be done in the next two weeks, and the report is important to be written nicely and everything captured.
[0:20:32] Shuhei: Yeah, I
[0:20:32] Sadiq: want you to keep getting stuck into modeling that takes a while, and the rewards are not guaranteed. Yeah, so yeah, just finish the last thing and report as it is. I mean, to whatever you found up to that point, and that's it. Yeah, yeah. That's it's not an easy topic, you know. You did a lot compared to the previous work, we just took the result as is. We
[0:21:08] Shuhei: okay, perfect. Yeah, we'll see. Okay, so next week we'll probably hopefully have the report drafted. Which guys? Yeah, that's probably the best timeline. Yeah, yeah, yeah. I mean, I'll run a couple more simulations with that. And one more thing that I do want to add is because I've added. So I guess in terms of complexity or more realism, I added like the roughness. I'll add actually if you could. I'll just take a note of that roughness.
[0:21:44] Sadiq: You see, there is a. I'll show you. There is a. If you look at Moody chart, have you heard of Moody chart? No. It's for fluid mechanics.
[0:21:57] Shuhei: Because I'm going to run the the entire simulation with the new roughness, and then and then because it's significantly more rougher than what I was running, I think it would actually reduce the liquid going out of the steam outlet.
[0:22:17] Sadiq: Yeah,
[0:22:20] Shuhei: yeah, no. The
[0:22:21] Sadiq: Moody in fluid mechanics Moody chart give you how to calculate friction in pipes and different equipment. Okay. Let's see.
[0:22:50] Shuhei: Moody charge. Oh wow! Moody charge. Moody charge is basically
[0:22:53] Sadiq: you have friction factor, and this is roughness height. Roughness. Okay. Eta, and this is different material. So this is commercial steel, which is what we use. Commercial steel, 045 millimeter.
[0:23:11] Shuhei: Could you maybe please send
[0:23:13] Sadiq: this? Yes, sure.
[0:23:15] Shuhei: And now quickly. So yeah,
[0:23:18] Sadiq: here this is relative roughness, which is eta over d d is diameter of the pipe. This is flown pipes. Remember, it's it's not exactly what you do, but the roughness roughness is how rough is the pipe. Meaning that the wall of the pipe is this is the wall. Normally, it's made of a lot of rough bits and pieces. I'm exaggerating here, so this point and the highest point, you know, any surface is not even this is not smooth. There's roughness to it. For example, glass is zero because glass is very smooth when it's clean and fresh. Concrete is way very rough, right? Yeah. Point nine to nine, and you have to finish. Yeah. Wood. Wood or something, something. So yeah.
[0:24:13] Shuhei: Okay.
[0:24:14] Sadiq: So commercial steel is this. That's
[0:24:17] Shuhei: us. Yeah. Point oh four five. Yeah. I the the most I modeled was I think point 008 so like in nowhere near like a quarter less than a quarter of so
[0:24:28] Sadiq: you are already
[0:24:30] Shuhei: yeah just reply what would work yeah perfect yeah yeah so I. I guess, I guess in terms of like the bucket list things that I still want to do before actually finalizing everything, is obviously one with the new roughness. I'll remodel the rerun the simulation with the new roughness. I think that would, at the moment, there's about with the with the current newest model that I have, it's about three kg per second of liquid going out of the steam outlet, so around 97% removal efficiency, but that's still really low, right? Like it's not like the actual separator is much more efficient at removing liquid if I'm. It's around like yeah, so I think increasing the roughness I would hopefully get closer to the realistic value, but also I haven't properly modeled like re-enterment. So obviously the wall film could get picked up by the steam again or the turbine and and split off or
[0:25:39] Sadiq: yeah rejoin
[0:25:40] Shuhei: yeah rejoin, or if there's like a, for example, the the inlet, there's a wall where like it disconnects, so like splitting and getting carried away again, like all these like small I guess droplet activities with,
[0:25:55] Sadiq: yeah, I mean something you maybe you can if this is the inner part and this is the shell.
[0:26:01] Shuhei: Yeah.
[0:26:01] Sadiq: Okay. And that wall arrive here, right? Yeah. And then it splits and go here. Maybe we make something from the outside, like a cut, to remove them and bring them down from the outside, so we don't affect the roughness of the inside of the wall. It's accumulating here. We have a
[0:26:28] Shuhei: so like essentially another pipe for the liquid to grab. Yeah, something
[0:26:31] Sadiq: like this on the top.
[0:26:34] Shuhei: Yeah, that makes sense.
[0:26:38] Sadiq: On the layer and it goes down and then enters down. and go outside from the outside. You can have a pipe going from the outside back down.
[0:26:47] Shuhei: Yeah,
[0:26:48] Sadiq: and that collect all that moisture.
[0:26:52] Shuhei: I'm not sure if I can model that. No, you can suggest don't model it. Okay, you can suggest
[0:26:59] Sadiq: that so you remove that layer that keep traveling, which is right now six kg or whatever.
[0:27:04] Shuhei: Yeah,
[0:27:04] Sadiq: and yeah, so there is a flow to that six kg, right? Some flow rate. Right now, six kgs are on the wall. Yeah, but how much keep building and how much arrive out of this? Not all the six kgs is possibly less.
[0:27:22] Shuhei: Yeah,
[0:27:23] Sadiq: but it just keep moving. Some of it go down, but some of it keep going up. And that bit that goes up, if we collect it, you can improve. Stop, stop particle jumping.
[0:27:38] Shuhei: Yeah, 100% You could,
[0:27:41] Sadiq: you can just suggest that.
[0:27:43] Shuhei: Okay,
[0:27:44] Sadiq: and for future work and
[0:27:45] Shuhei: yeah, for future. Yeah, okay. But yeah, I'll I guess. And
[0:27:50] Sadiq: but the the those bars that you welded on the, if you can run them or no.
[0:27:56] Shuhei: Oh yeah, I can 100% run them probably by the end of today.
[0:28:00] Speaker 1: Yeah, yeah.
[0:28:02] Sadiq: Okay, I think that's that's about it. To be honest, as we can just now writing a nice report and capturing all these, and you show that you've done it systematically, tried this, you tried increasing the flow rate slowly, tried to look at stability of solution, tried different solvers and so.
[0:28:22] Shuhei: Yeah, yeah, yeah. Okay, yeah. Hopefully, we did develop a little bit of more understanding on how this
[0:28:29] Sadiq: works. You guys did. Yeah, it's not a straightforward problem, but they pushed it further.
```

</details>

