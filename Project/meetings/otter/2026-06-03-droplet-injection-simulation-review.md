---
otter_id: "v-3_1o3rA4ZGDFH0wVpBiFlsa_o"
source_url: "https://otter.ai/u/v-3_1o3rA4ZGDFH0wVpBiFlsa_o"
source_start_time: "2026/06/03 19:04:29"
source_timezone: unspecified
imported_on: 2026-10-12
---

# Droplet Injection Simulation Review

| Field | Source value |
| --- | --- |
| Date and time | 2026/06/03 19:04:29 (timezone not supplied by connector) |
| Duration | 18m 51s |
| Source | [Otter recording](https://otter.ai/u/v-3_1o3rA4ZGDFH0wVpBiFlsa_o) |

Imported from Otter.ai. The summary and action items are Otter-generated; they record the meeting and are not verified project results. Original speaker labels and wording are retained. File dates use the timestamp supplied by Otter, without timezone conversion.

## Otter summary

The team discussed the simulation of droplet injection, focusing on the mass and size of droplets. Speaker 2 reported initial tests with a student edition, noting inaccuracies and limitations. They used 3 million nodes in a professional setup, achieving a flux efficiency of 99.95%. The highest efficiency (37%) was observed with 5-micrometer droplets, while 1-micrometer droplets had only 11.5% efficiency. The discussion included the impact of droplet size on efficiency, the need for better meshing and simulation settings, and the importance of balancing steam and water flow rates to improve efficiency.

## Otter action items

- Speaker 1 - : Update the simulation setup to include droplet injections with steam in the steam inlet, so that the droplets are injected directly with the steam flow rather than as a separate post-processing step.
- Speaker 1 - : Refine the simulation setup (meshing and solver settings) to achieve a near-perfect mass balance between inlet and outlet flows before proceeding with further efficiency analysis.
- Speaker 1 - : Compute the separator efficiency using the standard definition (mass of steam out divided by total outlet mass) and provide this standard efficiency alongside the current count-based efficiency for comparison.
- Speaker 1 - : Expand the discrete phase model injection study to include additional droplet sizes between 10 and 50 micrometers (including 50 micrometers) in addition to the current sizes, to better characterize the efficiency curve.
- Speaker 1 - : Investigate and recommend appropriate discrete random walk, rotation, and drag-law settings for the DPM injection model to simulate more realistic droplet behavior.
- Speaker 3 - : Send the referenced paper (e.g., via a copy or picture) by email to the requester so it can be used as a reference in the work.
- Andy - : Package the Workbench project files into a single archive file and send it to the team member who requested it.
- Andy - : Bring a USB drive containing the Workbench archive file to the next meeting so it can be plugged into the meeting computer.

## Full transcript

<details>
<summary>Show the complete speaker-attributed transcript</summary>

```text
[0:00:03] Sadiq: Plus the whatever mass storage of those droplets, so what's the total mass of those droplets that are escaping?
[0:00:16] Shuhei: So we inject more droplets that does go up, because with his sizes, right,
[0:00:25] Sadiq: the if you use, if you're going with the smaller part droplet sizes, have more of those smaller drops. Yeah,
[0:00:35] Shuhei: I did test them out, so I guess I could show you some of this reset up, but the first day I just did it at home, so they're kind of inaccurate. So these are some of the stuff that I did at home, but because I, because I was using the student edition, I could only do like 170 88 guys, and I think the accuracy was quite off, but we, I kind of was able to test it out, and this is how I kind of figured out
[0:01:05] Sadiq: this, this bit, this the ring here, so this is just one of the
[0:01:13] Shuhei: injections where I did 1.29 to the four size,
[0:01:20] Sadiq: what the red means is,
[0:01:23] Shuhei: so this is based off of time. So this is with two discrete random walk on with two iterations. So essentially starting from the exact same point, there's two possible path, there's just two iterations. So one of them, they both kind of just end up being on the wall, so where red is is where the particle ended up
[0:01:44] Sadiq: here.
[0:01:45] Shuhei: Yeah,
[0:01:46] Sadiq: but these particles, when they end up at the ring at the top, which is what happens, you know, you have a pipe going and that's on the on the shell, there is those particle running, and then they will jump eventually, because you can't just keep things having them accumulating, they will jump and go with this team, but I'll just go to the final setup that I just
[0:02:10] Shuhei: kind of finished, which is the one that actually ran the professional setup, so it should be a long way here, so the professional film set up, I did want my
[0:02:19] Speaker 1: 3 million nodes, so like 10 times more than what I did at home,
[0:02:22] Andy: zoom into the, yeah, so this is kind of the geometry that I'm working with now. So this is the steam, and this
[0:02:29] Shuhei: thin little bit is the water, so it's pure two phase now. Earlier, when last week I was kind of doing like a mixed two phase, right? So now it's purely two phase with the correct in mass flow, so this small, yeah, is the liquid, yeah, the rest is all steam, yeah, the rest is all steam, yeah, but the mass flow rate of water is huge, but yeah, so when I calculate the flux, this is, I guess, so I am getting so with that size,
[0:03:03] Sadiq: yeah,
[0:03:03] Shuhei: yeah, I'm getting, I guess, the correct four kg,
[0:03:07] Sadiq: 14 kg per second of steam of liquid,
[0:03:11] Shuhei: liquid is oh no, 116 point
[0:03:16] Speaker 2: decimal is to this
[0:03:18] Shuhei: is just straight from the flux report, that's why, but
[0:03:33] Speaker 2: when you are going to show the report, you know that two or three,
[0:03:41] Shuhei: yeah, so that was 116 for the liquid inlet, and then zero for steam, and then for steam inlet zero for liquid, and 81.64
[0:03:50] Sadiq: Well, we talked last time. How about you include some droplets with this team?
[0:03:55] Shuhei: Yeah, so so that's what I did for the injections. So at the moment I just ran the simulation with and then do the injections later, so and then, so just purely off the flux efficiency, there was actually quite a bit of unbalance, like the solution didn't really converge well, because there was a steam out, you know, sort of like they got a full, so there was more steam coming out than going in, so that's definitely an issue with my simulation, so yeah, if you could possibly maybe help us with, I don't know, how to converge better, whether that's my meshing issue or my simile issue, I'm not 100% sure, but just going off with this step now, the just purely on the flux, the efficiency was 99.95
[0:04:42] Speaker 2: How did you calculate the efficiency?
[0:04:44] Shuhei: So, like Sadiq said, so all the
[0:04:48] Speaker 2: outlets
[0:04:50] Shuhei: I had an equation
[0:04:52] Speaker 2: outlet divided by liquid inlet,
[0:04:57] Shuhei: the steam out plus the. Go down, I think. Yeah, so, yeah. Total out,
[0:05:03] Sadiq: yeah, total mass flow rate of steam. Total,
[0:05:05] Speaker 2: what it says is different.
[0:05:08] Shuhei: So, the top
[0:05:11] Speaker 2: is the liquid carryover
[0:05:14] Sadiq: fraction. Yeah, that efficiency is reasonable. It's a good start, a good start. So,
[0:05:22] Shuhei: yeah, so the dryness is, I guess, the total steam, the total mass going out of the steam happening.
[0:05:34] Sadiq: Dryness is different from efficiency. Efficiency or dryness equals one when it's 100% efficient, most, yeah, most of the time the efficiency,
[0:05:45] Shuhei: I guess, is
[0:05:47] Sadiq: x minus is mass of steam divided total, mass of steam plus mass of water, which is what you've had in efficiency is mass of steam valued by mass of steam plus mass of carryover.
[0:06:11] Speaker 3: Yeah, and
[0:06:14] Shuhei: then I guess, because obviously with the size of the penalty tried, we couldn't get them to go out, so I tried different types of, I guess, chocolate sizes, so I guess one micrometer repentance like super, super fine, was kind of impossible, and then some of them, so the next one I tried was a five micrometer, which is, I guess, kind of the still on the lower end of chocolates, I
[0:06:41] Sadiq: mean, you expected a small, the small ones that will come
[0:06:45] Speaker 1: out is
[0:06:46] Sadiq: the 50 micro, 50 micrometers, that's these are the endless, of course, other ones are will never, as long as the steam is going, it's just they go with the steam, they don't have time to fall down,
[0:07:02] Shuhei: yeah, yeah, so I guess technically, so I just ended up trying one 510 4100 micro meters, and then I guess the so these I've only tried 200 parts, so I don't think that's enough for like a full on report, but at the moment I just want to hopefully test out 400 watts and
[0:07:26] Sadiq: working in mass, okay, that mean, so let's say 20 microns, and how much weight the total of those,
[0:07:36] Shuhei: I'm actually not too sure that we can do,
[0:07:41] Andy: we have the density
[0:07:43] Sadiq: sphere with the density of water, and we can also increase the density beyond the density of water, because it sometimes carry mineral, so it's heavier than normal water. We'll look into that heat, right? Simple, changing the weight of the droplet, make it heavy, because it has mineral, silica, salt, calcium, chloride.
[0:08:12] Shuhei: Yeah, definitely be able to do that for next week, or actually, but yeah, at the moment we're just trying with the water density, and I guess the result I got was the four five micrometers. I got the highest, actually. I'm not too sure why it was higher than one micrometer, but 37% of the 200 injected went out. One micrometer, actually only 11% or 11.5% went out, so I'm not too sure why that is the case, but and then 10 point finally was 7% and then at 41 I'll try, I guess I should probably try more in between, from 10 to 4150 yeah, in the 50 as well, but from 41 it was just,
[0:09:05] Sadiq: and that's the efficiency,
[0:09:07] Shuhei: yeah. I guess so, yeah. The
[0:09:11] Sadiq: same way we talked here,
[0:09:12] Shuhei: so this is just purely calculated based on for how many escaped and how many were still in the thing, or went to the bottom.
[0:09:20] Sadiq: No, use use this calculation for efficiency. Okay,
[0:09:25] Shuhei: so rather than just purely on the number of the keep this for now, as so we understand, but also have this. Okay, yeah, definitely will be able to do that. And then, because I wasn't too sure with the DPM settings and injection ceilings, because there's like a discrete random walk, and like rotation, and all the drag coefficient, drag laws, stuff like that. I kind of just like roughly tried a different one for five micrometers, so the deterministic baseline is both discrete random walk and like rotation and drag law. Is turned off, which was around 32% by now, and then with this free random walk, it was only around 20% and then with rotation only was around 34.7% I'm not sure what this tells, but if you could maybe help us out on which injection settings to turn on and off to, I guess, simulate a more realistic particle, I guess.
[0:10:26] Speaker 2: Yeah, yeah, that would be a little bit concerned about why when you increase the size of the particle, your, you should expect to decrease the percentage of the escaped, yeah, so yeah, but why from one to five it increase, and five to decrease. I'm not too
[0:10:49] Shuhei: sure why it's happening, yeah, that's probably something to do with going back to the imbalance with the dispersion.
[0:11:00] Sadiq: We should get a perfect balance before we, so definitely, yeah, but I mean you're in the right direction, you know. Wow, is
[0:11:09] Shuhei: would it be okay for us to, I guess, test the efficiency based off like this, just testing out first, looking at the floods. This is
[0:11:18] Sadiq: so you know what you, what you're trying, how much, but I also want you to calculate the other way, which is because that's what people judge, that yeah, this is how it's judged in the field, but for you, for numerical, if this is what you want to see, where your particles are going, yes,
[0:11:37] Shuhei: yeah, it's just simply easy,
[0:11:40] Sadiq: easy for you to see. Yes, when the particles are tiny, they are more likely to escape, which is shown here. If they are heavy, more likely to be separated, but it is - it is slightly different from reality. We expect a bit more carryover in all aspects, it's too efficient. Maybe the imbalance,
[0:12:07] Shuhei: yeah, some definitely something to do with the meshing of some settings that needs to be defined. I think, but I guess I roughly, where kind of is it? Would it be okay for us to? I guess, yeah.
[0:12:19] Sadiq: Oh, yeah, you're on the right track in the students,
[0:12:21] Shuhei: yeah. And I guess we have kind of filled it with some turbulence methods.
[0:12:29] Sadiq: Let's keep looking at the water that accumulates in that ring. Where does it go if it just keeps accumulating? So
[0:12:35] Shuhei: I guess I also brought this class for how the particles move around motion depending on the size, I think. What size was this? So this is for the five micrometer. It was so most of them does go. So last time, how there was like a ring up here, and it didn't go above. Yeah, so I guess for smaller particles it does.
[0:13:02] Sadiq: Yeah, so when those particles that trapped here, yeah, they were likely to fall straight into the steam pile. Yeah, and that's just like when you go to a Turkish bath, there's always droplets stuck to the wall they fall on you and you are like this something similar to push back to try this, so this
[0:13:29] Shuhei: is just like and then this is online and then so I guess the size as size increases I guess so it's going it's getting kind of lower and then this less particles up here, which is, I guess, a good sign.
[0:13:48] Sadiq: So it's interesting. Sorry, you see that. How many turns the steam enters here? One spin, second spin, and the third spin. If we slow down the flow, will it do more spins? How many times it spins with
[0:14:10] Speaker 2: change the speed of the inlet? What happened to the
[0:14:14] Sadiq: how many times it spent two, three to go up. So, and we relate that because we know for a fact from field when we slow down the steam efficiency improve, but we are greedy. We want to put all our steam in a small vessel, save us money, and so this thing we can try at not much once we kind of refine everything, we can just slow the steam, put less steam, keep the proportion by reduced steam, reduce water, and see what it does, and how that affect efficiency. So, because I chased the industry, I'm still chasing them, going to a conference next week. And I'll chase them for data, but we can look at the fundamentals of this, if we, if we run it fast, double the mass flow rate of both, it will have less spins to come up, maybe move, and then it to track, there's an analytical model that basically, what it does is analytical model, you know that walls of the outer wall, it opens them and see the trajectory of the particle on the wall, as if it's a plane wall, and it just see, so you see what angle it takes, because this is going in an angle, right? Yeah, because I'm talking about the particle that flows on the wall, they go slower, right? Yeah, because the friction and everything, and there's an angle where it climbs,
[0:15:53] Speaker 4: as
[0:15:53] Sadiq: if it's.. if you open the vessel as a plate, it's a straight line, more or less, so we can look into that. Just a simple equation, you can put in Excel, or whatever.
[0:16:14] Shuhei: So, Adam, if you could maybe help us with the. this
[0:16:20] Sadiq: is good. We are on the right track. Let's just forget about matching his, you know, that was done. I don't know, maybe he did something, because I've been asking him, asking him to send me, and send me this bit with this, this thing, and I'll send me this, he sent me this with the missing something, you know. We can't just,
[0:16:43] Shuhei: yeah, I think, yeah, I think we can work with, we have that problem here, hopefully.
[0:16:49] Sadiq: So have your own efficiency, but give us the standard efficiency to compare, so you know where all your particles are going, but how does that translate into separator efficiency?
[0:17:08] Andy: Can I ask your help in finding me this paper? Actually, because I don't think I can't find it online. You referenced it in one of your past papers, I think.
[0:17:20] Speaker 2: Going to,
[0:17:21] Andy: yeah,
[0:17:21] Speaker 2: bring the bring that in the reference.
[0:17:38] Maedeh: Did you search in Google Scholar?
[0:17:43] Andy: Yeah, I did. Um, it's not like the PDFs, all about GRC
[0:17:46] Sadiq: transactions. Yeah, yeah, copy, picture, send it to me in an email.
[0:18:02] Andy: Oh, yeah, and then give you the actual workbench files. Yeah,
[0:18:06] Speaker 2: archive file. It's not possible to send me the workbench file, because each workbench has heaps of files. If you just go to file and save as archive, it gives you some kind of zip work page file.
[0:18:26] Speaker 1: Okay,
[0:18:26] Speaker 2: and then you can send it to me, just one single zip
[0:18:30] Speaker 5: file.
[0:18:30] Shuhei: Would it be possible for you to plug in? Yeah,
[0:18:33] Speaker 2: you can bring your USB.
[0:18:35] Andy: Yeah, we have it. Oh, he has that
[0:18:42] Speaker 2: meeting. Meeting next week is
[0:18:46] Speaker 6: your overseas, okay? So, do you
[0:18:49] Maedeh: want to
[0:18:50] Shuhei: have.
```

</details>

