---
otter_id: "vpyzRG9jRua8Hv5vefR_JOB56Y4"
source_url: "https://otter.ai/u/vpyzRG9jRua8Hv5vefR_JOB56Y4"
source_start_time: "2026/04/22 19:06:34"
source_timezone: unspecified
imported_on: 2026-10-12
---

# Wk 6 - Spiral Inlet Design Meeting

| Field | Source value |
| --- | --- |
| Date and time | 2026/04/22 19:06:34 (timezone not supplied by connector) |
| Duration | 19m 3s |
| Source | [Otter recording](https://otter.ai/u/vpyzRG9jRua8Hv5vefR_JOB56Y4) |

Imported from Otter.ai. The summary and action items are Otter-generated; they record the meeting and are not verified project results. Original speaker labels and wording are retained. File dates use the timestamp supplied by Otter, without timezone conversion.

## Otter summary

The meeting focused on the design and modeling of a spiral inlet for a separator. Speaker 1 provided the CFD model and discussed the homogeneous mixture of water and steam entering the spiral inlet. The inlet conditions were clarified, with water on the outer side and steam on the inner side. The team discussed simplifying the model by assuming a constant water level and open outlets. They also considered the impact of heat loss and condensation on the separator walls. The next steps involve modifying the inlet boundary conditions, running simulations, and comparing results with the homogeneous model. The goal is to improve the model's realism and address practical issues in separator design.

## Otter action items

- Speaker 0 - : Contact the company contact Energy to obtain a detailed design case for their new large separators for use in the CFD model.
- Speaker 0 - : Call industry contacts to obtain a real-case separator design that can be used to update the CFD model with realistic dimensions and operating conditions.
- Speaker 1 - : Modify the CFD inlet boundary conditions to represent separate water and steam inlets, using the existing spiral inlet geometry as a starting point.
- Speaker 1 - : Review the spiral inlet design file and, if needed, modify it to match the updated inlet configuration for the CFD model.
- Speaker 1 - : Run the first CFD simulation with the modified inlet boundary conditions and compare the results with the previous homogeneous-mixture case.
- Speaker 1 - : Use the base-case separator enthalpy of 1600 kJ/kg from the paper to calculate the dryness fraction and mass flow rates for the water and steam inlets, and keep this enthalpy constant for the initial runs.
- Speaker 1 - : Run the new CFD model with the updated boundary conditions and save the results for later comparison with the homogeneous-mixture case.

## Full transcript

<details>
<summary>Show the complete speaker-attributed transcript</summary>

```text
[0:00:03] Speaker 1: Have react design, but it looks like the spiral inlet is there. Also, okay, beautiful, yeah, you're going to figure that out to work. You I don't have, I don't have your email. Oh, it's S, Y, OK. Sy, OK, four for three. Yeah, here we go. Yes, perfect. Thank you so sorry. Media can't make it today. She needed to go to her daughter's school. I know. So I've got the file here, yep, okay, thank you. And so I've emailed my gang guys, because what I have is the bank map, CFD model, yes, and I told him, can you send me the spiral inlet? So he already sent me something. He said, For the spiral inlet design, I use this design for my window, which is his field for my project. The folder name is CW, W, computer design the file have been available in the previous name, however, a voice copy from the CW. So, yeah, okay, so let me go see, let me go to the folder again and see if I so, as we said, in terms of where your work is different From his, fluid went as a homogeneous mixture. We are going to inlet our fluid as two separate so the inlet into the separator, which is like a square. You split that water and steam, and it enters. You know? What enters the spiral? Yeah. Then that you have at this boundary condition here, you have water here and steam, okay? And then they go and mix them, whatever they like to do. And then hopefully that that's the whole key in this approach.
[0:03:26] Speaker 2: I did actually ended up making it the spiral one a little bit, but I don't know if that's like, I would end up using the one that gave
[0:03:35] Speaker 1: us, but yeah, so you see the inlet condition here?
[0:03:38] Unknown Speaker(s): Yes, yeah, I wasn't doing that.
[0:03:41] Speaker 1: That's all right. That's okay. So here at the inlet, here, when it comes in, right now, it's mixture, homogeneous, yeah, you see, see, here you inlet. The inlet here is water on this side, on the outer side, and steam on the inner side.
[0:04:01] Speaker 2: Yeah, okay, yeah. So that kind of, I guess, simulates the centrifuge.
[0:04:07] Speaker 1: Yeah, because, yeah. Because what happens is the pipe move up and start to go this way. It's already been separated in the pipe going in and throw the water to the outside. So by the time it gets here, there's more steam. There's, of course, some water with the steam and some steam with the water. But yeah, most of the water is on the outside at the end and and that's, this is what we like to try, yeah, yeah.
[0:04:39] Andy: Can I ask some clarifying questions. So the way we're modeling it now, we're like, our domain is so in the paper, you're assuming that the water level is constant.
[0:04:54] Speaker 2: So you Yes, so like, there's no, like, brine outlet. It's just,
[0:05:00] Speaker 1: ah, yeah, just like a open tank on the bottom,
[0:05:05] Unknown Speaker(s): yeah, that's fine. You cut it off.
[0:05:07] Speaker 1: So, I mean, you want to complicate. This is to simplify, yeah,
[0:05:11] Andy: yeah, no, it's okay. But I just want to clarify. So, did you model that as a war, or is that another outlet?
[0:05:18] Unknown Speaker(s): This is so this and this are open outlet, outlet, yeah, outlet, okay, okay, this is where the steam comes, a steam outlet. And that's like, fluid, yeah?
[0:05:30] Speaker 1: So instead of putting this to simplify, yeah, all the water can go here,
[0:05:35] Unknown Speaker(s): go out there, yeah? So one's a pressure out there and
[0:05:39] Speaker 3: one's a mass. I think both is pressure, right? Yeah, pressure, both outlets.
[0:05:44] Andy: Pressure, okay? Because that's one point, um, I wanted to clarify, because I was doing it as a pressure. I was doing it where that was a war, and then so like mass was accumulating inside the floods, yeah, so that's not correct.
[0:06:15] Speaker 1: Cool, if you look at one of the other diagrams we had the at
[0:06:24] Unknown Speaker(s): the one before, yeah,
[0:06:28] Speaker 1: yeah, here, there is no, if you zoom in, there is no outlet. So that's the boundary, yeah? That circle the disk,
[0:06:37] Unknown Speaker(s): but, but we model it as
[0:06:38] Speaker 1: an outlet, yeah? These are outlet. The whole disk is an outlet. Yeah, reality, we shouldn't, of course, but this is simple. That's not our focus, because you see in separators, what happened is that the separator,
[0:07:02] Speaker 3: so it's complicated to and that's, that's the actual outlet.
[0:07:06] Speaker 1: Yeah, outlet is here and, and the steam comes out here. Okay, so this is steam. This is inlet steam. Go here, come out. Water comes out here. But here in this area, sometimes pieces of rock and junk fall. And from time to time they have above, they blow it up, open it, throw the rocks and too much detail, because our focus is the quality of this team here. How good the quality of this team with the homogeneous model that was done, it shows it's super fantastic. You don't have a problem, but we are getting a lot of problems in real life. And so, okay, yeah, you reminded me. I'm going to call a company contact energy. They're having already problem with their new big separators, and maybe we can get a case like detailed design on their separator. You can play with it. It will involve just changing some dimensions and bits and pieces in your model, pressure and blah, blah, but it's more or less the same.
[0:08:20] Unknown Speaker(s): Yeah, okay, yeah, okay. So I'll start by changing the inlet and for the water and then the air.
[0:08:30] Speaker 1: So basically, the steam goes this way, and there is a skirt around it, while water disappear. We don't want to know what we are focused on, quality of steam. Yeah, that steam that has the dryness makes sense. Sound good, yeah, sounds good. Look into that file. You know those files? Yeah, take your time. No, no, yeah, yeah, look at them and see what. Yeah, looks like you can modify this pile. So if he didn't send the exact design, yeah, we should be okay, yeah,
[0:09:20] Speaker 2: yeah, yeah. I'll definitely, we'll definitely ask you more questions if we if more comes up, yeah, that's why I'm here. But at the moment, I guess that's about it.
[0:09:32] Speaker 1: Yeah, we want the CFD to be more realistic, representing the real thing, so in that model, assuming the walls of the separator, these walls of the separator are perfectly insulated. In fact, there is some heat loss, which can cause some condensation, so we can maybe slowly complicate the design data. Let's get the first initial run with this modified inlet boundary. See how we behave, compare it with the homogeneous and then we take it from there.
[0:10:16] Speaker 2: Okay, yeah, oh, actually, one of the question I have is, so when we set the two inlets and for the for the mass flow and stuff, should we just use some of the values that's listed on this paper to just kind of Yeah, because I'm not sure how much like water and how much air we should
[0:10:39] Speaker 3: it's like 13 years ago, yeah, yeah,
[0:10:48] Unknown Speaker(s): I was living in New Zealand. Can you, can you take me this way? Yeah, okay, yeah, just two fingers will. Mm. Him.
[0:11:07] Speaker 1: So you see, that's the enthalpy in the separator pressure when he came here,
[0:11:15] Speaker 2: and this is the flow of the liquid and the gas. So would it be fine to just use these values for now?
[0:11:22] Speaker 1: Yeah, we can calculate them. Very simple. Okay. So, so you have the enthalpy, which you can do, any enthalpy. We measure that enthalpy in kilojoules per kilogram. I think the base case is 1600 Okay, okay, then they calculate dryness, fraction, assuming perfect separation, which comes enthalpy, this minus HF. Did I give you steam tables? I again, whoa, we don't have to remember, obviously. G now, what's this? Is that enthalpy? Okay, yeah, this is the enthalpy. This is enthalpy of liquid at the separator pressure, which, in this case, with the separation pressure is 11.2 right? So you go to this steam table. Go 11.2 bar absolute, 11.2 bar absolute, absolute. And this one is what he was changing like here in that table. Yeah, he went up. So when he get x, and then the mass of steam, M, dot, steam equals m, dot, total times x. And that's so that's what he calculated, mass flow rate, mass of steam. Okay, okay, yeah, so the higher the enthalpy, the more steam, the lower the enthalpy, okay, okay, okay, okay.
[0:13:20] Speaker 2: We just okay. We'll start with the 1600 and keep that constant.
[0:13:24] Speaker 1: If you look at the steam table, let me keep it so that steam table is basically works like this. If you know the temperature, yeah, you have the saturation, pressure, enthalpy, entropy, density. You don't need those if you know the pressure. There's another table at the back, pressure, a function of pressure, water and steam property function of pressure. And so you go to an event here. So this is 11. This is 12. That's the enthalpy of liquid, HF and hfg. I don't have 11.2 but you can interpolate from these. Okay, yeah, okay, you put them here, you calculate x when you know x, mass of steam is mass flow rate total times X.
[0:14:33] Speaker 2: Okay, so it's 12 bar. Okay, yep, that's a lot of information.
[0:14:46] Speaker 1: You don't have to memorize. You just get what you want, go down the table, pick up what you want and plug it in the calculation,
[0:14:55] Unknown Speaker(s): can I just take a photo? Just take take the paper
[0:15:02] Speaker 4: and a photo.
[0:15:22] Andy: Okay, just one last clarifying questions, actually. So it says that the inlet pressure was 11.4 bar and outlet was 11.2 Yes. So, I mean, I know that that top thing would be 11.2 But would this thing also be 11.2
[0:15:43] Speaker 1: more or less? Yes. Okay, so it's
[0:15:46] Unknown Speaker(s): just mostly about the internal
[0:15:49] Speaker 1: pressure, yeah. So that it 11.4 comes in here. Okay, there's a bit of pressure, drop, Steam, travel, go down here. So the separator, the pressure inside the separator is the same fixed. And so here and here are exactly the same. Well, maybe there's a bit of hydrostatic head on top of this, but it will be too small to matter. That's why he didn't model it really deep, you know, because there will be a more head on the water. You it makes sense. And if we in your modeling, once you we like to look at what you know, we want to zoom and see what happens on the walls. Because any moisture, any moisture that builds on the wall. So not fluid entering here, right? Steam will start Spin, spin and enter here, right? So there will be steam traveling on the walls. There's a bit of layer of film, right? My and that film, because the steam is moving up and turning that films also gets pushed, pushed slowly, much slower, yeah, than the steam, but it spirals up, and sometimes at the end, it go block trouble with the with the steam, and go down.
[0:17:12] Speaker 2: Yeah. I kind of drew something like that. Obviously, this model is not very accurate, but this kind of like a small contour, yeah, something like this,
[0:17:27] Speaker 1: like something like but this is too big. What is this right now? Sorry, can you tell me
[0:17:32] Speaker 2: 9.3 5e minus three, which is, what is it? This is the volume fraction of the of the water.
[0:17:44] Unknown Speaker(s): Yeah, volume fraction, which is which? I wasn't too sure. I just got
[0:17:50] Speaker 1: so volume fraction is similar. You can multiply by density and get mass fraction. Yeah, well, it's very small, right?
[0:18:01] Unknown Speaker(s): I think. So, yeah, 10 to the minus 10 to the minus three.
[0:18:08] Speaker 1: So what's the unit volume fraction? Fraction is dimensionless? Yeah, okay,
[0:18:16] Speaker 2: but I'm pretty sure this isn't that accurate. But I would try with the actual new
[0:18:22] Speaker 1: boundary conditions that should be the focus. Run the new model as it is and keep it for you to later on, compare with the other model. Yeah. Okay, okay, yeah, sounds good. That's everything. Yes, me, Okay, I'll try. I'll call some, make some calls in the industry, and try to get a real case this time. Thank you for New Zealand. This is very old, from Indonesia. 12 years ago. I.
```

</details>

