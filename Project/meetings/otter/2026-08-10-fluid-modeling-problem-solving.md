---
otter_id: "h_ahpzlwj3unFGKkFAyAqbKJC-o"
source_url: "https://otter.ai/u/h_ahpzlwj3unFGKkFAyAqbKJC-o"
source_start_time: "2026/08/10 15:18:06"
source_timezone: unspecified
imported_on: 2026-10-12
---

# Fluid Modeling Problem Solving

| Field | Source value |
| --- | --- |
| Date and time | 2026/08/10 15:18:06 (timezone not supplied by connector) |
| Duration | 5m 52s |
| Source | [Otter recording](https://otter.ai/u/h_ahpzlwj3unFGKkFAyAqbKJC-o) |

Imported from Otter.ai. The summary and action items are Otter-generated; they record the meeting and are not verified project results. Original speaker labels and wording are retained. File dates use the timestamp supplied by Otter, without timezone conversion.

## Otter summary

The team discussed issues with a model lacking a brine outlet, leading to poor continuity and non-steady liquid states. Andy proposed using user-defined functions to remove liquid at a constant water level, but found insufficient liquid reaching the critical area due to lack of pressure or gravity. Shuhei is conducting DPM mass sensitivity tests to determine how much liquid mass is carried by droplets. The basic solution's accuracy is questioned, and the team plans to revisit the model with a brine outlet and examine different equations and geometries. They agreed to update the team via email.

## Otter action items

- Grten3 . - grten2@gmail.com : Over the next week, investigate alternative turbulent flow equations and revisit the model geometry with a proper brine outlet to reduce continuity residuals and stabilize liquid mass, then report any improvements observed.
- Grten3 . - grten2@gmail.com : Send an email to clarify which equations are being solved in the simulation and set expectations about the project versus the course assignment context.

## Full transcript

<details>
<summary>Show the complete speaker-attributed transcript</summary>

```text
[0:00:02] Andy: Okay. Great. So essentially, what is happening is we've discussed this briefly at the start of the the at the start of the the project. Basically, with how it's modeled right now, there's no brine outlet, so there's the continuity residuals obviously very bad, and now we found out that like liquid is basically like it's not, it's not really steady state. So as the iterations keep going, so this is from 4000 to 6000. Yeah, the the the the the mass of liquid increases, so that's not right. So we've basically been trying things to fix that. The obvious solution is obviously to model the right outlet itself, but I thought maybe before that I should try. I found out that you can write somewhat user-defined functions. So essentially, what I wanted to try first was say if because the current assumption is like where we cut it off is where there's like constant water level. So if liquid hits around that cell, there's a function that just like removes it. So I wanted to try that first. So, ah yeah, and that's just like visual confirmation of like liquid sort of. So that's the volume fraction, and you can see it. It increases, yeah, from 4000 to 6000 iterations. But essentially, I try that with the here. That's picture better. So basically, whatever liquid that touches there gets removed. That's the the simplification. But turns out that's like not really enough because I think the main problem is not enough liquid actually reaches that part there, because you know there's no. I think like gravity is the only thing that's that's driving it down, because there's no hole, there's no like pressure or anything that actually pushes the the liquid down there. So that's like sort of the the path lines that confirms
[0:02:28] Speaker 1: it. Have you tried to stand it about this problem?
[0:02:32] Andy: No.
[0:02:33] Shuhei: We only really thought. Yeah. Yeah.
[0:02:36] Andy: I mean, I messaged you guys briefly on
[0:02:39] Speaker 1: that, but it's better to send an email in certain teams. Yeah, he's not a Teams person. Yeah,
[0:02:51] Andy: yeah. Yeah, yeah. I mean, yeah, I was.
[0:02:54] Speaker 1: So your problem, in the simple wording, your problem is not following the continuity law. Yes.
[0:03:00] Andy: So I think I think so. I think after doing all this stuff, the basic conclusion is I think we have to model it like properly.
[0:03:10] Shuhei: So the the
[0:03:12] Speaker 1: just back to the Rue's question: What kind of equ Ruse asks you a question in the part for project versus here? What equation you are solving? If you can find, this is a turbulent equation. If turbulent equation, what sort of equation? Maybe it's better. It's it's it's a good way to understand all the parameters, and maybe it helps you to find where is yeah where is the error is coming from, where the error is coming from.
[0:03:41] Shuhei: Okay. So maybe it's not just the geometry, but rather the equation as well. Okay. Yep. And then what I was doing is, I guess because now we, I'm trying the one with, I'm just doing DPM mass sensitivity, so we have the liquid you on the wall, so that from the liquid inlet, and then with the steam, some of the droplets are being carried. And I'm just really testing out, okay, how much of the total liquid mass is being carried by the droplets. So I'm just really just seeing, okay, if it's like at 5% how much droplets are escaping? If it's at 10% how
[0:04:23] Speaker 1: much changing the parameter?
[0:04:24] Shuhei: Yeah, just only changing the droplet mass. Sensitivity
[0:04:27] Speaker 1: analysis. Yeah,
[0:04:28] Shuhei: sensitivity analysis, and I mean, I guess I'm just seeing what I'm supposed to see. Yeah.
[0:04:33] Speaker 1: But before before putting a comment on your word, because still you are not.
[0:04:41] Shuhei: Yeah, yeah. So the basic. So the
[0:04:43] Speaker 1: basic, the fundamental of the solution. Yeah. The basic solution is is not right. We can say that. Without that, you cannot do sensitive analysis. Make sure first. The first step is. Yeah. You know.
[0:04:58] Shuhei: Yeah. Yeah. So maybe for the next week we'll spend it looking at other equations and then also maybe looking at the geometry stuff as well to see to maybe because at the start we were trying to model it with the brine outlet as well. So maybe we'll go back to that and then see how that changes again. It was
[0:05:18] Andy: really complicated. That's why we we move back to this for now, but turns out it's like it's not really correct. Yeah, so we're kind
[0:05:26] Shuhei: of like taking a step backwards a little bit, but yeah,
[0:05:30] Speaker 1: yeah.
[0:05:30] Shuhei: So that's kind of the state right now. Okay.
[0:05:32] Speaker 1: Yes. For update. Yeah. Send send an email to set it in the lane. Yes.
[0:05:38] Shuhei: Okay. Easy.
[0:05:40] Speaker 2: Yeah.
[0:05:40] Shuhei: Sounds good. Okay. Okay. Yeah, that's about it. Sounds like a plan. Functions and geometry
```

</details>

