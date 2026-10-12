---
otter_id: "AdOJ45dAl8IN8Q8Qmse8VkPusdI"
source_url: "https://otter.ai/u/AdOJ45dAl8IN8Q8Qmse8VkPusdI"
source_start_time: "2026/05/27 19:05:13"
source_timezone: unspecified
imported_on: 2026-10-12
---

# Model Validation Meeting

| Field | Source value |
| --- | --- |
| Date and time | 2026/05/27 19:05:13 (timezone not supplied by connector) |
| Duration | 26m 39s |
| Source | [Otter recording](https://otter.ai/u/AdOJ45dAl8IN8Q8Qmse8VkPusdI) |

Imported from Otter.ai. The summary and action items are Otter-generated; they record the meeting and are not verified project results. Original speaker labels and wording are retained. File dates use the timestamp supplied by Otter, without timezone conversion.

## Otter summary

The team discussed issues with a model simulating DPM injections, noting that despite setting up the liquid droplet injection based on a paper, they are not achieving the same steam quality. They examined pathlines and flux reports, finding a 97% efficiency but no escaping particles. They plan to adjust the inlet conditions and consult with Maria for insights. They also considered testing with a small mass flow rate of particles directly injected into the steam to see if any particles escape. The goal is to match the results from a previous paper, which showed particles escaping, despite the current model not showing this behavior.

## Otter action items

- Andy - : Ask Maida for suggestions on why the current CFD model is not behaving the same as the Panunto model, focusing on the particle injection and overall setup.
- Speaker 1 - : Set up an Excel sheet to implement the analytical efficiency model from the paper so that simulation parameters can be compared against it.
- Speaker 4 - : Update the CFD inlet setup to use separate pure steam and pure liquid inlets with area ratios proportional to the volumetric flow rates, and compute the flux-based separator efficiency for this new setup by next week.
- Speaker 4 - : Coordinate with Maida (by next week) to review the CFD model and particle injection setup, including sharing the model and having her run it to help diagnose why droplets are not escaping into the steam outlet.
- Speaker 4 - : Run a trial CFD simulation injecting small droplets (with a small diameter and increased mass flow rate) into the steam inlet to see whether any of them escape into the steam outlet.
- Speaker 4 - : Compute the separator efficiency from the flux report and compare it against the analytical efficiency model from the paper to validate the simulation.

## Full transcript

<details>
<summary>Show the complete speaker-attributed transcript</summary>

```text
[0:00:02] Andy: Well, since he's on us
[0:00:03] Speaker 1: the files from the past week, the model, I guess we've kind of played around with it, and he just ran it, and then what you can tell and what you did,
[0:00:14] Andy: so I've.. sorry, no, it's not on
[0:00:22] Speaker 1: here. What do you want to see?
[0:00:23] Andy: Um,
[0:00:26] Speaker 1: so basically, since we have his model, like the only thing,
[0:00:30] Andy: like it's all set up, so like we're able to open this, so that was good, but the liquid droplet, the DPM injections wasn't set up, so like I just set that up based on his paper, still, but like for some reason we're still not getting the steam quality that he's getting in that no particle is escaping when you inject.
[0:00:57] Speaker 2: Can I have a look?
[0:01:00] Speaker 1: I mean, mine's not the same, but we can kind of extrapolate from what we have. I mean, yeah, sure, yeah.
[0:01:10] Andy: So, well, this is just the pathline, so it's actually that,
[0:01:14] Speaker 2: yeah.
[0:01:14] Andy: So, essentially, when you, when you, this is like just the pathline. So, I think what you mentioned, like chemical traces,
[0:01:21] Speaker 2: yeah,
[0:01:21] Andy: like, like that's basically what that
[0:01:23] Speaker 2: is,
[0:01:23] Andy: I think, and I think that still shows that, like, like there's still a
[0:01:30] Speaker 2: path,
[0:01:31] Andy: right, like there's still like a flow field that leads
[0:01:35] Speaker 3: to the, yeah, to the outlet, yeah,
[0:01:38] Andy: but when you actually do it with like particles, like with mass.
[0:01:42] Speaker 1: This pipeline is based on just the field alone and has no effect. The mass hasn't, like this has no mass,
[0:01:52] Andy: but when you actually calculate the droplet diameter and mass and all that, nothing escapes.
[0:02:01] Speaker 1: Yeah, so this is essentially the, yeah, so this this pathline is based on the time, so where it's red is where it spent the most time. So from the simulation is not the exact same, because this is with the two phase setup, but it shows that it's red here, so that means it's kind of getting like
[0:02:22] Speaker 2: a layer of stagnant, yeah, right,
[0:02:26] Speaker 1: yeah, and it's so this, these particles are actually escaping, but when you do the injection, most of them just
[0:02:33] Speaker 2: kind of around, yeah,
[0:02:34] Speaker 1: yeah, so
[0:02:35] Speaker 2: of course you can't just accumulate and sit here, they have to go somewhere, right,
[0:02:39] Speaker 1: yeah, so, yeah, that's kind of
[0:02:42] Speaker 2: so, so here, do we have the, that here is the liquid,
[0:02:46] Andy: yeah, that's the, that's a cut off, so we're back to cutting
[0:02:50] Speaker 2: it off, okay, yeah,
[0:02:51] Speaker 1: so that's just like transsuming, as yeah, when when it hits the bottom, it just gets trapped at the moment,
[0:02:58] Speaker 2: okay, can I look at the entry, the geometry of the entry? Yes,
[0:03:06] Speaker 1: yeah. So that was his. He just tested it with essentially nothing changed from the model, and he wanted, we wanted to see how the injection and everything does. But yeah, so I'm just spraying it in half, and then, but because of the density difference and everything, I can't just do pure steam and then pure liquid on this side, otherwise, because of the density difference, the velocity, and I thought that calculation kind of went through it, but yeah, I couldn't do pure liquid and pure steam if I do like a half car, so obviously in the future I can do like a perfect ratio, where it's like because the density is so different between the steam and the liquid, I'd have to do the liquid would be a lot more, I guess the inlet area would be much, has to be much
[0:04:01] Speaker 2: smaller.
[0:04:02] Speaker 1: Yeah,
[0:04:03] Speaker 2: so let's, let's calculate how much. What it should be, it doesn't have to be 5050
[0:04:17] Speaker 1: Yeah, yeah.
[0:04:17] Speaker 2: So, what's enthalpy? He's using
[0:04:19] Speaker 1: 1600
[0:04:21] Speaker 2: yeah. and what's the separation pressure? 1.4
[0:04:25] Speaker 1: What was it? It was a GPA. Inlets one point
[0:04:30] Andy: 1.14 mega pascal, and outlet was 1.12 mega pascal,
[0:04:36] Speaker 2: 1.4 1.14 Four
[0:04:40] Andy: 1.14
[0:04:43] Speaker 2: MPA,
[0:04:44] Andy: yeah,
[0:04:46] Speaker 2: so for this, and what's the total mass flow rate? You know,
[0:04:51] Speaker 1: yeah, so that
[0:04:53] Speaker 2: is
[0:04:53] Speaker 1: the total total is 197 point 61197 61197 This is actually not. This is off by a little bit, since I miscalculated a little bit, but it's off by like 112 kgs.
[0:05:11] Speaker 2: Okay, 197
[0:05:13] Speaker 1: Yeah, so 197 should be
[0:05:15] Speaker 2: you check later. So let's find out what's how much mass of this and mass of that going in, which equals H separator minus HF at this pressure minus HFG at this pressure. This is the this is the enthalpy of liquid at this pressure. This is the difference between enthalpy of steam minus enthalpy of gas at this pressure. So, look at the steam table. We don't have it exactly at one point. We might have to interpolate, I is 11.4 right bars, because we talk in bars.
[0:06:07] Andy: Yes,
[0:06:09] Speaker 2: there's 11 and there's 12, so point four, so then I'll be somewhere between here, let's say we have to interpolate between this and this, so 600 minus HF at 11.4 which is basically interpolate this is enthalpy of liquid, enthalpy of steam, and this is the difference, just the difference between this minus this, because that's what we need here. Okay,
[0:07:01] Speaker 1: so are we trying to calculate the mass flow of the liquid? And
[0:07:05] Speaker 2: yes, no, we have
[0:07:06] Speaker 1: - we, we did calculate based off of the pennants paper, so it should be right. But yeah, this is just straight from the paper, so as long as
[0:07:16] Speaker 2: you know this is rock.
[0:07:19] Speaker 1: This is all this is this is just calculating the rough steam quality at this inlet.
[0:07:24] Speaker 2: Yeah, that's wrong, because that here x this is he already have the masses,
[0:07:31] Speaker 1: yeah.
[0:07:32] Speaker 2: So he already has the mass of liquid, mass of steam,
[0:07:35] Speaker 1: right? Yeah, so I'm just based off of his paper.
[0:07:39] Speaker 2: Oh, okay.
[0:07:40] Speaker 1: At the 16,600
[0:07:42] Speaker 2: trying to calculate, there's no
[0:07:45] Speaker 1: need. Yeah, so he did all the calculation for us. So, yeah, we just based off..
[0:07:49] Speaker 2: so, so there is this is kilograms per second. This is kilograms, so this much liquid, this much steam. Yeah, this. yeah, you're right. If you multiply by density to get the, to get the volume right. Sorry, volumetric flow rate equals m dot, right, which is kg per second times or divided by kg per meter cube, so you divide the liquid by the density of liquid and velocity m dot liquid m dot steam equals m dot steam divided by rho steam. Okay, so that's the volume,
[0:08:53] Speaker 1: right? So it's m dot for
[0:08:55] Speaker 2: the overall m dot steam overall rho. You can get it from the steam table here,
[0:09:01] Speaker 1: yeah, so M dot steam of a poster,
[0:09:04] Speaker 2: yeah, yeah, did you do that?
[0:09:06] Speaker 1: Yeah, so M dot steam of a row steam, yeah, yeah, so that,
[0:09:10] Speaker 2: sorry,
[0:09:11] Speaker 1: oh, this is, I did it, but
[0:09:13] Speaker 2: yeah, so this much meter cube per second off, so this is
[0:09:19] Speaker 1: liquid, and this is a steam, and this is the total.
[0:09:22] Speaker 2: You just sum them up,
[0:09:23] Speaker 1: yeah, yeah. And then is
[0:09:26] Speaker 2: that what you fit in? Your doesn't have to be a split, it can be,
[0:09:31] Speaker 1: yeah,
[0:09:32] Speaker 2: can be this much liquid. The rest is steam.
[0:09:35] Speaker 1: Okay,
[0:09:35] Speaker 2: yeah, yeah. I, I didn't, sorry, yeah, it has to be specific to this case. What we're trying to say is they enter one liquid that is system, and they go inside.
[0:09:48] Speaker 1: Okay, yeah, yeah, I can definitely set that up easily, but at the moment I was a bit.. I just did a half, or at least for the assimilation,
[0:09:57] Speaker 2: of course, it's different. If it's half,
[0:09:59] Speaker 1: there's
[0:10:00] Speaker 2: more liquid, right?
[0:10:01] Andy: Yeah, it's gonna be more liquid.
[0:10:03] Speaker 1: Oh no, I calculate the volume fraction based off the area, so it should be the amount should be the same. Well, amount should be what's here. So, yeah, I chucked in the volume fraction for so given the half, so one side was pure steam and the other was a mixed combination of steam and liquid, and I put in the specific liquid volume fraction, so that the mass flow rate for the total is still the 190 7.6 and it's the same.
[0:10:34] Speaker 2: Why don't you have all liquid here, no matter how much it is? Yeah, volume, the rest is all steep.
[0:10:41] Speaker 1: Yeah, I didn't initially think of splitting it in ratio, such that areas like that.
[0:10:50] Speaker 2: It's not exactly like that,
[0:10:53] Speaker 1: but yeah, that's 100% what I'm going to the next. But at least for this setup, I didn't think that far at the moment, so I just did a half, half, half,
[0:11:03] Speaker 2: yeah, because half, half, you've been putting too much liquid, less steam,
[0:11:06] Speaker 1: no, no, I did, I did put in the right amount of liquid and steam, because
[0:11:11] Speaker 2: this
[0:11:12] Speaker 1: is not pure steam, oh purely good, yeah, it's still
[0:11:16] Andy: volume, yeah,
[0:11:17] Speaker 1: exactly, so
[0:11:18] Speaker 2: have them separate, yeah, okay, separate, regardless, whatever the volume fractions, this is liquid, yeah.
[0:11:27] Speaker 1: So it's kind of like semi two phase, semi two phase, yeah.
[0:11:33] Speaker 2: And
[0:11:34] Speaker 1: then, and then I guess out of this, from the simulation, this is kind of the flux report that I got. So, how much, how much mass we put in, and then how much steam came out, and all that stuff, and yeah, these are some rough numbers, but well, not rough, but this
[0:11:56] Speaker 2: is what we, the steam is high, the liquid is not much,
[0:12:00] Speaker 1: yeah, so, yeah, so out of the steam outlet, steam that much steam came out, and then this much liquid
[0:12:06] Speaker 3: came from the bottom.
[0:12:08] Speaker 1: No, actually, no, this, this went through into the steam
[0:12:11] Speaker 2: with the steam,
[0:12:11] Speaker 1: yeah.
[0:12:12] Speaker 2: Ah, that's what we want to see. Yes,
[0:12:13] Speaker 1: yeah, except for the fact that, so obviously, from the flux report, there is liquid going out from going into the steam right, but when we do like the particle injection,
[0:12:25] Speaker 2: yeah, you don't see that,
[0:12:26] Speaker 1: yeah, I don't, we don't actually see any of it, because from just purely off the flux report, and when we do the efficiency purely off the flux report, we get around 97% or from this simulation, I got around 97% efficiency,
[0:12:40] Speaker 2: yeah,
[0:12:40] Speaker 1: so that means at least 3% of the droplets should be going through to the steam out there,
[0:12:45] Speaker 2: right? That's what we want to see.
[0:12:47] Speaker 1: Yeah,
[0:12:47] Speaker 2: if you think the droplets, the particles is not showing it, the calculation is what we want to see. Yeah, that's fine.
[0:12:55] Speaker 1: But yeah, so and then one way Pananto really, because flux report is just, you know, there's not much, I guess, mass, like it's not actual droplets really going it through. So the way Panonto did it was to actually inject
[0:13:14] Speaker 2: the droplets, yeah.
[0:13:16] Speaker 1: So these are kind of, I guess, the specific metrics of what kind of droplets we injected, but yeah, after testing like a bunch of different setups, well, we didn't see any of the particles going out, so yeah, that's kind of the issue we're stuck on right now, I guess. Yeah, we just don't see any of the particles, even though we, because of the flux report showing that the actual particles don't actually go out of the, yeah. steam and yeah, so I guess I guess I don't know
[0:13:50] Speaker 2: this is this is progress,
[0:13:53] Speaker 1: yeah, I guess if
[0:13:58] Speaker 2: you try just leave the particle track for a second. Let's, let's go back and change, correct the inlet conditions
[0:14:05] Speaker 4: a bit.
[0:14:06] Speaker 1: Yeah,
[0:14:06] Speaker 2: and see what the efficiency of the separator comes out to be. It should be more efficient, I guess, based on everything saying the same, but you know, to be proven and everything. yeah. Talk to mind about why the particle, yeah, is not working.
[0:14:30] Speaker 1: Yeah,
[0:14:31] Speaker 2: share your model with her, you know, just so she can see why, because based on obviously there's water going with the steam, based on the flux. How do we track that water? How do we.. where is that water going?
[0:14:55] Speaker 1: Yeah, yeah, I'll start off by, yeah, splitting it into actual pure steam, pure liquid. Make sure the areas are nice, and I guess proportional. But yeah, yeah, I'll definitely talk to my dear, hopefully tomorrow, or as soon as possible, regarding to see if the injections and just overall set up of things. Hopefully, that can get us a little bit more context and help on the regards, I guess, but yeah, some nice contours and stuff, I guess.
[0:15:31] Speaker 2: You always get nice contour,
[0:15:33] Andy: so this is the
[0:15:35] Speaker 1: how the velocity vectors look like in the
[0:15:39] Speaker 2: overall
[0:15:40] Speaker 1: style,
[0:15:41] Speaker 2: yeah. or
[0:15:43] Speaker 1: the steam kind of going into
[0:15:45] Speaker 2: the.. oh, sorry, that's the steam,
[0:15:47] Speaker 1: yeah.
[0:15:48] Speaker 2: Where is the
[0:15:49] Andy: pipe that's at the outlet? Yeah, this is the top of the outlet. This is
[0:15:53] Speaker 1: so the outlets here, and then this is just showing just, yeah,
[0:15:57] Speaker 2: okay,
[0:15:59] Speaker 1: yeah. And then you can kind of cedar as well, and then this is the inlet, so it's, it's nice and smooth. There's no, you know, I guess the geometry matches, it's nice and smooth, so that's at least that's good. Yeah, and then these are the part time we talked about earlier, yeah. And, yeah, another issue is just what's going on around here, where the particles do spend a lot of time here, so I'm not sure
[0:16:27] Speaker 2: that what happens if there's a particle thing, because this particle been kind of pushed all the way to the top, and then eventually you have this layer of liquid there, they separate from the wall and fly with the steam, yeah, and they become those droplets eventually, yeah. Okay,
[0:16:48] Speaker 1: maybe we don't have enough accumulated, I don't know,
[0:16:54] Speaker 5: yeah,
[0:16:58] Speaker 1: but yeah, I guess, yeah, I guess we're just stuck on the injection part, and yeah, that's mostly the main part.
[0:17:06] Speaker 2: Let's restable progress. Let's, let's do the inlet and see what the party, and kind of see what that impacts the efficiency of the separator, and talk to Maida about the model, so take send her the model, and see if she runs it, so you can explain a few things. How do we, how we get a better match, and or how do we get it to behave? What this mean, the ring of water at the top, where does it go? Maybe sometimes the numerics make the water disappear somewhere, when it doesn't
[0:17:46] Speaker 5: like
[0:17:47] Speaker 2: some dispersion or something.
[0:17:50] Speaker 1: Yeah, okay, yeah, definitely talk to Maria about that. Yeah, you have any, any more
[0:17:59] Speaker 2: questions?
[0:18:00] Andy: Nothing to add. We'll talk to my day asap.
[0:18:03] Speaker 1: Yeah,
[0:18:03] Andy: modeling.
[0:18:05] Speaker 1: Yeah. So, okay. For hopefully by next week, I'll have.. well, I will have the new inlet, and I'll calculate. I'll definitely be able to calculate the efficiency just purely based on flux, but I'm not too sure what's going to happen with the injection, hopefully my day can help us out with that, but yeah, hopefully we'll have that by next week. Yeah, actually I have
[0:18:30] Speaker 2: the flux that the you can check the flux against the analytical model in that paper.
[0:18:36] Speaker 1: Yeah,
[0:18:37] Speaker 2: you know the efficiency based on the flux, compare that with the analytical model.
[0:18:45] Speaker 1: Okay, okay, yeah.
[0:18:46] Speaker 2: And see the change that you're going to do with the inlet, will it impact the analytical model?
[0:18:55] Speaker 1: Okay, yeah, okay. So you just test it against the analytical as well. Yeah,
[0:19:03] Speaker 2: okay. Can stick it in Excel and use it, and just use it to compare what our parameters here, there. Analytical is not
[0:19:13] Andy: just a
[0:19:13] Speaker 4: rough
[0:19:14] Speaker 2: estimate, not perfect. Otherwise, that's why we don't rely on it. That's why we're coming to CFD to try to see what happened. Are you doing this for
[0:19:25] Andy: me? Yeah, I guess I'll probably.. I'll definitely ask my dear about this too. But do you have any suggestions? Like, I don't know, for me, for like, why we why, like, I'm still not getting it to behave the same as the Panunto model.
[0:19:53] Speaker 1: Yeah, because, yeah, the biggest, I guess, mystery we have is that, because he's just running the exact same setup as the one that he did in the paper, and we're not getting, I guess, the same results
[0:20:07] Andy: on mine. It's just all I've never managed to get any particles to escape, so I mean, yeah, with the with the out to the steam outlet,
[0:20:23] Speaker 2: yeah,
[0:20:24] Speaker 1: so yeah,
[0:20:26] Andy: yeah, it's just it's 100% always I've tried so many different like parameters for the for how we model the particle injection,
[0:20:38] Speaker 4: maybe we find a different solver, do you know what solver he used last time, but I have no idea,
[0:20:47] Andy: like model,
[0:20:48] Speaker 2: model equation.
[0:20:54] Andy: Oh, yeah, yeah, all of that is the same, because I have his model that you gave me, yeah, so it's just the way you model the particle injections now, but yeah, we've tried like a few different setups, like five, six different setups, still 100% steam quality with the
[0:21:16] Speaker 1: particles,
[0:21:21] Speaker 2: with the particles,
[0:21:22] Andy: with the particles, yeah,
[0:21:23] Speaker 2: the flux is,
[0:21:25] Speaker 1: yeah,
[0:21:25] Speaker 2: reasonable,
[0:21:26] Speaker 1: purely flux, his one should, yeah, come out close to, yeah, yeah, I'm not too sure, yeah, okay, but
[0:21:36] Speaker 2: is the mass flow rate of the particles you're injecting is significant to show a difference or
[0:21:45] Andy: the mass flow rate of the particle of the particle, so the particles is is divided into like nine nine injections, and the distribution is it's based on the
[0:22:03] Speaker 1: so we're just testing these nine different with these diameters and this much flow, so total should match up the using,
[0:22:14] Andy: so it's based on that distribution, the calculation, so yeah, it all adds up to the liquid flow
[0:22:21] Speaker 2: rate,
[0:22:24] Speaker 1: yeah, and this way it should be a lot more accurate way of calculating the efficiency,
[0:22:36] Speaker 2: so he's injecting everything in tiny particles with this diameter from this to this, which is very small, right?
[0:22:43] Andy: Yes,
[0:22:45] Speaker 2: and so all those particles in your model, they already become liquid and go liquid,
[0:22:55] Speaker 1: just get stuck on the wall, and just, yeah, yeah.
[0:22:58] Andy: Well, in his paper, he did mention that a lot of them is unresolved, like, like even after the time runs out, the path is still like not completed, because it's still spinning around instead of being tapped at the border, so he just assumed that those were like trapped
[0:23:20] Speaker 2: with the liquid at the bottom,
[0:23:22] Andy: but I mean, yeah, it's, it's not like it matters to my case, because, like, none of them's escaping
[0:23:30] Speaker 1: anyways, so yeah, even when we test, because obviously the smaller it is, because it's less, I guess, mass, it should be closer to, I guess, steam, so it should be easier to go into that, yeah, yeah,
[0:23:43] Speaker 2: that's the intention,
[0:23:45] Speaker 1: yeah, but even when you, when you test, like, yeah, I guess the smallest size particles, it just everything, yeah,
[0:23:51] Andy: yeah, so even when I drop, like, I made that 1.29 to the power of negative 10, I mean, negative five instead of negative four, you know, make it behave more like a, like a massless, you know, tracer
[0:24:04] Speaker 2: timing,
[0:24:05] Andy: so even that still doesn't go out, which is really weird.
[0:24:10] Speaker 2: Yeah, we need the Midas magic on this one. Yeah, yeah, yeah, getting somewhere with this, so
[0:24:21] Speaker 1: Hopefully we can figure out something with the injection by next week after discussing with my dear, and I'll definitely have the setup done by next week.
[0:24:33] Speaker 2: The way I look at it is that flux is going, the droplets are going here separately with this with the liquid with the steam, sorry, so small, so this is as is, but these droplets are very small quantity, let's say one kilogram per second or something, and they go with the steam,
[0:24:58] Speaker 1: okay, okay,
[0:25:00] Speaker 2: rather than we end, we enter nine different particles and see where they go. Not all that model basically assume all my liquid is particles with that range of diameter, right? Enter as spheres, right? Yes, you know, and they just go with their diameter, and some go with the steam, some don't.
[0:25:27] Andy: Yeah,
[0:25:27] Speaker 2: if we, if we use that new calculation, but have, let's say, one kilogram, two kilogram per second of particles in the steam going in with the steam, add it on top, though we can adjust the masses later on.
[0:25:45] Speaker 1: Yeah,
[0:25:45] Speaker 2: just as a trial, have them tin you in the steam, see where they go there.
[0:25:50] Speaker 1: Okay, okay,
[0:25:51] Speaker 2: not entering as all liquid,
[0:25:55] Speaker 1: yeah,
[0:25:56] Speaker 2: because now we have two separate, separate inlets, liquid and steam, but the steam carries tiny droplets.
[0:26:04] Speaker 1: Yeah, okay, okay, okay. I can definitely test that out. Yeah,
[0:26:10] Speaker 2: use whatever diameter, use tiny small diameter, and increase the mass flow rate to see if any of them going with this team,
[0:26:21] Speaker 1: yeah, just try to get any particles to go
[0:26:23] Speaker 2: to go with the steam, just so we can see.
[0:26:25] Speaker 1: Okay, yeah, yeah, that can do that. That'll be interesting, yeah.
[0:26:32] Speaker 2: Okay,
[0:26:33] Andy: yep, that's all for this week.
```

</details>

