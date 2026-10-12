---
otter_id: "LVcOkUHW5ReOjB4ohNarurmSu70"
source_url: "https://otter.ai/u/LVcOkUHW5ReOjB4ohNarurmSu70"
source_start_time: "2026/07/22 17:43:09"
source_timezone: unspecified
imported_on: 2026-10-12
---

# Geothermal Simulation Analysis

| Field | Source value |
| --- | --- |
| Date and time | 2026/07/22 17:43:09 (timezone not supplied by connector) |
| Duration | 16m 39s |
| Source | [Otter recording](https://otter.ai/u/LVcOkUHW5ReOjB4ohNarurmSu70) |

Imported from Otter.ai. The summary and action items are Otter-generated; they record the meeting and are not verified project results. Original speaker labels and wording are retained. File dates use the timestamp supplied by Otter, without timezone conversion.

## Otter summary

The team discussed replicating Pernando Pernanto's results, confirming a baseline model. They explored inlet speed differences, noting a trend of lower outlet dryness at lower speeds. Shuhei tested different injection settings, including splashing, edge separation, and stripping, observing a 41% increase in wall film mass and thickness. They also discussed the impact of particle size on escape rates. The need for mesh refinement and validation against industry data was emphasized. Future steps include refining the model, ensuring consistency, and preparing a technical report with both numerical data and visual representations.

## Otter action items

- Speaker unknown - : Add a figure showing the wall film mass and average thickness versus time for the various wall film settings studied, so the trends can be visualized alongside the existing numerical results.
- Speaker unknown - : Extract and analyze the wall film results from the longer simulation runs to determine whether film thickness continues to increase or stabilizes, and provide an updated data point on this behavior.
- Speaker unknown - : Create contour plots for the different wall film cases (no wall film, splash only, edge separation, stripping, etc.) and send these contour images to the reviewer once they are ready.
- Speaker unknown - : Add a separate column in the results table that distinguishes between the base flux value and the actual DPM injection value, resolving the current ambiguity in the reported numbers.
- Speaker unknown - : Perform mesh convergence studies (mesh conversions) and adjust model parameters so that the outlet dryness and related metrics converge to realistic values consistent with prior research.
- Speaker unknown - : Prepare an additional simulation case with larger and smaller particle size distributions to investigate how particle size affects the fraction of particles escaping with the steam, and review this case in a future meeting.
- Speaker unknown - : Before upcoming meetings, upload the latest simulation figures and contours to Teams for the reviewer to review in advance, so they can come prepared to discuss them during the call.
- Speaker unknown - : Generate additional figures and visualizations (such as model screenshots and key result plots) to supplement the written report and meet the expected 4–6 page length.

## Full transcript

<details>
<summary>Show the complete speaker-attributed transcript</summary>

```text
[0:00:00] Shuhei: Which I'll go you through in detail now. But as a large caveat, we haven't done like mesh conversions, like all the fluent version studies or converge.
[0:00:11] Sadiq: Yeah,
[0:00:13] Shuhei: yeah. But we have some interesting values that we've found out through the experiments that we did. But yeah, so you you want to talk about the recreation part, or should I? Ah, so just briefly
[0:00:28] Andy: on replicating Pernando Pernanto's results, like that's like pretty much all done now. We basically got the same result as he did, so that's that's his. That's not his actual value because it wasn't in the paper, so we just digitize it based on the the the graph. But essentially, it's like the same.
[0:00:52] Shuhei: So we were able to yeah yeah replicate his thing. Yeah, yeah. It's a good baseline. Yeah. So so we have a
[0:00:58] Andy: baseline model.
[0:00:59] Shuhei: Yeah. Okay. So yeah, so now we kind of like have a place that we know that, and then you know the in the meeting we had like a couple of weeks ago, you told me about let's try inlet speed differences,
[0:01:13] Sadiq: yes,
[0:01:14] Shuhei: stuff like that. So I gave that a go as well. So here I did low reference high. So the Pananto one he mainly did 27.1 meters per second for the inlet velocity, so so I just used that as a reference value and I recreated it, and I got that outlet dryness. And then so at 20 so like you mentioned at lower speed, it was yeah, it was really good, and then it kind of lowered as the in the speed increased. So, yeah,
[0:01:48] Sadiq: yeah, yeah, fair enough. Yes, yes.
[0:01:50] Shuhei: So that's kind of the it's a right
[0:01:53] Andy: trend. Yeah, it's a right trend. The trend
[0:01:55] Shuhei: is right. It hasn't been. I would expect this to be
[0:01:58] Speaker 1: lower lower right lower
[0:02:00] Sadiq: wars. Yeah, maybe that's will show up in the refinements, English refinements. Yeah,
[0:02:07] Shuhei: but for now, I was I was kind of happy with the trend.
[0:02:10] Sadiq: Yes,
[0:02:12] Shuhei: yeah, and then after that, so so this is just like just checking different injection settings. I think I've already mentioned this in like a meeting like four weeks ago, but just as a nice simple report feature. So this is just essentially testing. So when you do the injection, there's different settings that you can do. For example, you can do you can I forgot the I forgot the settings actually did, but one of them would be like each injection would create 10 more possible like like 10 lives essentially. So goes into 10 times and then possibly take different paths. Like
[0:02:54] Sadiq: you enter as a distribution.
[0:02:56] Shuhei: Yeah, kind of like that. So it just even if it's just one injection, it's the exact same property, but it might take a different path depending on the continuity field or the field of the that. And I was just testing out how that affects the escape, how the DPM escapes. So that was just some sensitivity analysis on that, but it's not too significant at the moment because I haven't actually used this learning and applied it to other settings yet, but it's just a good knowledge to have, I guess, at the moment. And then after that, now we tried with solving the field. So we did the injection, not the injection. We solved the two-phase, the the the
[0:03:41] Andy: flow field. Yeah, the continued
[0:03:44] Shuhei: field, and now we just now we want. I wanted to when we do the injections, I wanted the injection to actually interact with the flow field, so that's what I did. So before it was the flow field was solved, and we'll just place the injections in, but now it'll be both at the same time, so the injections would actually
[0:04:06] Andy: influence. Yeah,
[0:04:07] Shuhei: it's influenced by
[0:04:09] Sadiq: the yeah the fill field is influenced by the yeah,
[0:04:13] Shuhei: and then I actually haven't made a graph for that, but with this, so I did that, and then I also added a wall film, so wall film is a big part of geothermal, right? So I thought that was a really important one, and so there are a couple of settings that we can turn on in the wall film. So for the control, we I did. So actually, I'll just talk about the settings that you could you can turn on. So in Fluent, you can turn on like splashing, so if the injection goes into the wall film, it splashes and then creates more
[0:04:46] Sadiq: droplets. Droplets.
[0:04:48] Shuhei: So that's one of the options. And another option is if you have like a sharp edge. So for example, the steam outlet, right? The steam goes in, and then there's like a, and then the outlay is here.
[0:04:58] Sadiq: Yeah.
[0:04:59] Shuhei: And then this is sharp edge. So if there was wall film here, there will be edge separation would occur,
[0:05:05] Sadiq: and then get sucked in. Yeah,
[0:05:07] Shuhei: that could happen, right? So that's one of the settings that I try test it out. And then another one, stripping. I actually don't fully understand what stripping does, but it's another way of I think. Oh no, I think what stripping does is, with the wall film, if there was enough turbulence, it would cause the film to, like the shear force would create enter
[0:05:31] Andy: back into the reentry. Yeah, I guess the flow.
[0:05:34] Shuhei: So those are the three wall film settings, and so the base case I didn't turn on any of these, so if the DPM just goes into the wall film, it'll just get absorbed into the wall film, and the wall film will just keep growing. And so, if we look at the settings here, so the control with no, so once the injection goes into the wall film, it'll just be absorbed. So it added up to about 07 kilograms, and then splash only, so splash
[0:06:03] Sadiq: per second or.
[0:06:05] Shuhei: So this is just like what's on the wall at the moment.
[0:06:09] Sadiq: All the walls. All the walls. Yeah. Okay. Yeah. So it
[0:06:11] Shuhei: just it's it either goes up or down.
[0:06:14] Sadiq: But that's what's at any time sits on the wall.
[0:06:18] Shuhei: Yeah.
[0:06:18] Sadiq: Yeah.
[0:06:18] Shuhei: Yeah. But yeah, and then so we can see that for if when we allow like edge separation, or stripping where the wall film can be dispersed because of the shear force and stuff like that, we can see that the the film actually loses mass because it's losing yeah
[0:06:37] Andy: entrainment right. That's the word entrainment.
[0:06:40] Shuhei: Yeah, and then when we so this is just combined. So it's just I'm just testing out a bunch of different settings, and we can see we can also see the thickness of the film, the average thickness of the film. So it's kind of correlated with the mass, which is good to know. But also, I need to add figure for this. But one thing I've realized is that for this initial conditions, I've actually I set the wall film to zero. So at the very start of the simulation run, there's no wall film, and then I and then with the inlet goes with the mass that it slowly builds up. But I'm not sure if that was the right approach. I'm still definitely looking into it because when I look at the contours and stuff like that, the wall film is developing, but it's quite localized and it's kind of spotty. Yeah, it's patchy, so I need to look into how should I be initializing it or should I be letting the simulation run way longer, so the wall film actually develops a little bit more.
[0:07:41] Sadiq: So right now, as you're running, what time does the film thickness increase or stabilize at some point?
[0:07:49] Shuhei: Well, at this moment, we this is all ran at like certain number iterations, so we can't I can't say that for sure. If you run
[0:07:57] Sadiq: for longer,
[0:07:58] Shuhei: maybe yeah. I actually does I actually do have all the simulation that ran like quite a bit longer than this at the moment, but I didn't have enough time to get the data, put it on here. So I'll be able to provide another data point where if the iteration count actually does increase or is it just stabilizing? So that's that, and then this part. So essentially, what this is comparing, so interaction off and on. So here earlier, they were we are going back to just solving the flow field with. So I I had injections here as well, but injection would weren't impact impacting. affecting the flow field, right? And then here I allowed it to the injections affect the flow field with the film wall. So here, actually, because because the injections keep getting injected, we see that when the interaction is on, the injections build goes into the wall film a lot more and increases the mass of the film a lot more. So yeah, we can see 41% increase in the mass of the wall film, and then the thickness also increases. The average thickness all increase at the same rate. Also, the speed of the film also increases, so that means that injection is actually applying more momentum into the wall film as well. Yeah, stuff like that. And then the splash events. There's more splash events when the injection is affecting the flow field, or when there's a lot more splash edge separation cases as well, because there's probably because there's more mass or there's more film, the more edge separation occurs. Same with the stripping events. Earlier there was none, but with injection actually affecting the flow field, there was a lot more stripping events as well, but yeah, at the moment that's kind of what we've done so far. But also at the same time, none of these are actually verified or validated, so it's we should all these values should be taken with skepticism.
[0:10:14] Sadiq: Yes,
[0:10:14] Shuhei: but I think we have some interesting values to work with.
[0:10:18] Sadiq: Yeah, do you have some contours when I see the different cases, or
[0:10:24] Shuhei: I haven't actually made those contours yet? Yeah, I can definitely send it to you once I make them. But at the moment, we only have the numbers.
[0:10:31] Sadiq: Fair enough. To be honest, let's let's look at. We will not be able to, if you know, to have measurement to confirm this because no one yeah
[0:10:43] Shuhei: no one decided to be cooked yeah
[0:10:46] Sadiq: so you have to kind of you've already validated your model against the old model and you're taking it further trying different things yeah yeah and that's that's that's absolutely fine. And I've tried. I've emailed the industry wanted some data. I don't think the data that will come will be anywhere near to support what you want.
[0:11:12] Shuhei: Yeah. But
[0:11:14] Sadiq: this is the things we say. This is outlook. You know, try to get the model. You know, with mesh refinement to as best as you can to show that it's stable and that's this is how we present it. Okay.
[0:11:27] Shuhei: Yeah. But you
[0:11:28] Sadiq: know, to be honest, yeah, from experience, the numbers you showed me earlier about the yeah, and it's quite
[0:11:35] Shuhei: off. Yeah.
[0:11:39] Sadiq: Here.
[0:11:40] Shuhei: Yeah, this one is too low or too high.
[0:11:43] Sadiq: This is too high. Too high. Too high. Yeah. Okay. Yeah. This is okay. I don't know, but this is too high. This is too low. They all need to drop. Even this one. Okay. A bit down. Go a
[0:11:55] Shuhei: bit down. Okay.
[0:11:56] Sadiq: Yeah. Yeah. That's that's from experience. Uh huh. Yeah.
[0:12:00] Shuhei: Okay. I think I actually needed to make another column. I I forgot this whether this was taken purely from the flux or the actual DPM. So that's definitely the ambiguity here. But I need to. I'll make another because the DPM injection is what really matters because those tell the story of how much mass actually escaped. Whereas this, I'm I'm not 100% sure. This might be the actual the DPM injection after the DPM injection, or this could just purely be base of flux, which is less reliable. Yeah. So I'll definitely advise on that one, and then try get similar values. Yeah. If you could send us possible like a roundabout number, or maybe those are already past research papers. Oh, we have, we do, we
[0:12:48] Andy: have those. Yeah. Okay.
[0:12:49] Shuhei: Yeah, we'll try to get closer to those then. Yeah. But yeah, that's kind of where we are at the moment. Okay. Yeah. So we'll probably start trying to, I guess, validate do mesh conversions.
[0:13:07] Sadiq: Yes.
[0:13:07] Shuhei: Yeah, and then also yeah, make it closer to realistic values.
[0:13:12] Sadiq: And the the particles that escape that comes out with steam. Do you can we see what size they are? Oh
[0:13:22] Shuhei: yeah, it actually has been written in this, but I can show you.
[0:13:27] Sadiq: Maybe we try a scenario using bigger, bigger particle sizes, smaller to inject. Because when the particles are big, I would expect less escape.
[0:13:40] Speaker 2: Yeah,
[0:13:41] Sadiq: when there are more to escape. Yeah,
[0:13:44] Andy: that's what we've been seeing.
[0:13:47] Shuhei: That's a good example that I can give you. Maybe it's in like these other sizes. but okay. I can't. I'm not sure if I'll be able to give you a moment right now, but
[0:14:15] Sadiq: maybe next time we can we look at them. Yeah, the actual
[0:14:21] Andy: contours and
[0:14:22] Sadiq: all the particles and
[0:14:24] Shuhei: yeah yeah sure yeah and you
[0:14:26] Sadiq: know you said on the walls the patches we want to see where they happening yeah okay
[0:14:30] Shuhei: yeah
[0:14:31] Sadiq: okay we can have a kind of predict where they normally happen and how
[0:14:35] Shuhei: okay yeah yeah 100% we
[0:14:38] Andy: could we could like send it to you like if you like on Teams before the meeting, and then we can like you can have a look at it if you have time first, and then we can just discuss
[0:14:52] Sadiq: it. Yeah, you know, in the meeting.
[0:14:54] Andy: Yep. Okay. Yeah.
[0:14:58] Shuhei: Yeah. No, I was a bit more focused on the technical media. There's a lot less figures. Yeah, yeah. They said how
[0:15:07] Sadiq: many six pages or six pages. Six
[0:15:10] Shuhei: pages. Yeah, yeah. Four to six.
[0:15:15] Sadiq: Yeah.
[0:15:16] Shuhei: But yeah, okay. I'll make more figures and stuff like that. Yeah. See where we can take forward. Do
[0:15:23] Sadiq: include anyway in the report a picture or two with the model. You can't just yeah can't just be numbers. Yeah. Yeah.
[0:15:31] Shuhei: True. Okay. Yeah. Right.
[0:15:36] Sadiq: Cool. Yes, that's that's fantastic. Yeah. I mean, we we're exploring, and then you trying different models is a good thing because I don't know which one works. Having help us choose best model in the future when we match data or someone comes to match
[0:15:56] Shuhei: data. Yeah, at the moment we just have a good setup to actually like try so many different setups at the moment. We don't. We haven't actually had solid like meshing convergence meshes to line up and then test in other cases. But we can at the moment we can test so many different setups. So that's just what I've what we've been doing. Yeah. You
[0:16:15] Sadiq: needed to explore all of these things to see, and then we refine and focus
[0:16:21] Shuhei: on the whatever is the if it's the
[0:16:23] Sadiq: most? And now we can go on non-mesh refinement to make sure that the answers are consistent and we say okay, the grease is for that that grid size is for. Yeah. Cool.
[0:16:37] Andy: Yeah. Sounds good
```

</details>

