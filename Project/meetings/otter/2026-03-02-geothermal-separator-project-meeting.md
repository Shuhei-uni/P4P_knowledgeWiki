---
otter_id: "Iwy7FmtbsQALliYfWmkXMbblN2U"
source_url: "https://otter.ai/u/Iwy7FmtbsQALliYfWmkXMbblN2U"
source_start_time: "2026/03/02 16:03:15"
source_timezone: unspecified
imported_on: 2026-10-12
---

# Geothermal Separator Project Meeting

| Field | Source value |
| --- | --- |
| Date and time | 2026/03/02 16:03:15 (timezone not supplied by connector) |
| Duration | 18m 31s |
| Source | [Otter recording](https://otter.ai/u/Iwy7FmtbsQALliYfWmkXMbblN2U) |

Imported from Otter.ai. The summary and action items are Otter-generated; they record the meeting and are not verified project results. Original speaker labels and wording are retained. File dates use the timestamp supplied by Otter, without timezone conversion.

## Otter summary

The meeting discussed the design and optimization of a geothermal well separator, focusing on a vertical cyclone separator. The current design, based on a 30-inch (0.75 m) diameter, struggles with larger separators due to increased droplet carryover. The team plans to use CFD modeling to improve the design, treating the inlet as two separate fluids (liquid and steam) instead of a homogeneous mixture. They will calibrate the model with industry data and explore flow regimes like wavy, mist, and stratified flow. The project aims to enhance separator efficiency to reduce water carryover and improve power station performance.

## Otter action items

- Speaker 0 - : Send the initial separator paper to the student and provide the CFD model files on a USB drive so the student can review the existing CFD setup
- Speaker 0 - : Provide access to the university compute resource (Nasi) so the student can run CFD jobs there
- Speaker 0 - : Schedule another meeting to include the overseas student when they return (arriving Monday next week)
- Speaker 0 - : Start and organize weekly half-hour catch-up meetings with the project students once the other student returns
- Speaker 0 - : Send additional papers and the IGA conference database link to support the student's literature review (ongoing delivery of resources)
- Speaker 2 - : Read literature and papers on separator design and two-phase flow to prepare the literature review for the initial report
- Speaker 2 - : Prepare and submit the initial project report that includes the literature review (as required by the project)

## Full transcript

<details>
<summary>Show the complete speaker-attributed transcript</summary>

```text
[0:00:00] Andy: Sorry about that. No worries. Should I close the door?
[0:00:14] Speaker 1: That project on separator? I'll send you that paper. You had a look. I had a quick look. Yeah, Master Student few years back did that. So what comes out of the geothermal well is normally, normally two phase steam and water, like gas and liquid, okay? And to what we needed the power station is just teams. We don't need the water. Water causes problems. So we have the separator. They come in a variety of designs, but that's the the optimum design, which is the vertical cyclone separator, or also what they call it, the bottom outlet, like a pressure vessel. Okay, there's a pipe that go inside. Okay, comes out this way. Fluid enter from here, which is the two phase. Liquid is heavy, so it inter tangentially, so fall down. There's a pipe to take the fluid, liquid from here, the steam, because it's light, goes this way and comes up. But they call bottom outlet separate, okay? And then that's been used in the industry for some times. There are some correlations on this paper I send you how to size it, but these correlations were based on a small design when the separator was 30 inch, which is about point seven, five meters diameter. Okay. Now the separators are getting bigger, okay, so what that result in more droplets going with the water? Which is not good. So what we want to do here is to see what we can do. We have that answers model available. I can put it the files. I can put them on and USB. Have you done CFD modeling last year? Yeah, okay, and my day is, will help you with the CFD modeling. I'll help you with the other side of the project, which is the calculations, the design, the story, and maybe we get some data from the industry to calibrate the model or not depends. So that's kind of the overall project we we on the user group.
[0:03:29] Andy: So has no one thought of using CFD to improve the design
[0:03:35] Speaker 1: before they used it. But the problem is, even with that CFD, we assume water and steam are a homogeneous mixture. When they are not they normally, the water is separated from steam. So as it enters the lower part is liquid, the steam is on top. So it's not as homogeneous, homogeneous. You can treat it as single phase, right? But in reality, it's not so. We hoping maybe we treat it as a at the inlet, as a two separate fluids, one liquid, one steam, and see what that does. I i Okay, so it's was done on fluent, Yeah, okay, so, yeah, you have a USB. I opposed.
[0:05:42] Speaker 2: Applause. You anyway, stuff on This, I You I
[0:07:40] Speaker 1: Okay? This says directory called CFD, geometry, mesh, fluid. And if you click on it, it will be Yeah, that's the I and check
[0:09:22] Speaker 2: Something for you. Some reason, I
[0:10:00] Speaker 1: man, a big file. Yeah, these are big files. You Yeah, so the mesh was making something grid block. But you don't have to run it. Only on your PC. We can get you access to NC ans, then you can run jobs there, sorry, on Nasi university computer, and we can run jobs There, see how we go. And you and you are the other student with you. Is he around?
[0:11:05] Andy: Or he's overseas right now? He'll come back Monday next week?
[0:11:12] Speaker 1: Yeah, we'll schedule another meeting, and maida should be there. Yeah.
[0:11:21] Andy: So like, is there anything that I can do right now, or I need to do right now this week?
[0:11:30] Speaker 1: Just read, read about separators, some literature, some papers. Literature on the design calculation you find at the back of the paper. Again, you said, yeah, so So the folder, there are other folders. These are my stuff. You don't have to worry something, something. So the USB plug, I have other stuff so the idea is, we see what's been done, see what we can because that was done more than 10 years ago. So software has improved, and resolution we can improve that. But again, the assumption, there are other papers were referenced here that uses, use CFD for modeling and but all the same concept. And they use also particle tracking, so they include some particles with the fluid and see how many go this way, how many to assess efficiency of separation. We can look at something like that, but we want to try model two phase as two phase. So two phase fluid is single phase, like water flow in the pipe. It's all water, if it's air, just air, but two phase is a mixture of both, and that can result in a variety of low regime. You could have wavy flow. You could have mist flow. You can have annual flow, where the fluid is all on the outside and the inside is steam. Or you have stratified where this is liquid and this is steam. Or you can have wavy, this is wavy and so on. So understanding flow regimes is important, and we want to try to change the inlet as two phase with one of those regimes, and see how will that impact our performance, performance of the separator, and what can we do to get it to work better? This is a big component of power stations. And you know, you go to power station, you see them really high, more than 10 meters high. And it's key, any small droplets of water going to the going to the turbine, what turns the steam and generate you cause problems to the turbine, turbine and damage. I'll send you some papers. I'll dig some papers on the impact of low quality steam. What's people been doing so you can include them in your literature review. So I know you need to put a report, initial report, right? You need to submit an initial report which will include your literature review. Okay, so I'll fire some stuff, and you look for other stuff that you can find in literature. Best place to look for the work in geothermal is the IGA database, IGA conference database, and you can search here under whatever you like, and it show you a lot of papers. You cannot use Science Direct, of course, or that's I'll send you that link.
[0:15:41] Andy: Do you use teams actively?
[0:15:44] Speaker 1: Not really, but if you want to send me something on teams, yes,
[0:15:49] Andy: I'm just thinking of like maybe an easier way to communicate, instead of just emailing every time
[0:15:58] Speaker 1: I check my emails all the time. Okay, works for me better. But I mean, if you want to schedule a zoom or team or con call, more than happy. You it's a good source of data, and I will slowly send you some papers to help you with the literature, because I know maida. She run the par four project, so she's the boss, so she will send email that you need to submit. Everyone need to submit an initial report, which includes your literature review at some point, and then we just follow that like everyone else. Okay, yeah, you you doing courses now, right? Yeah, drop by if you, you know, if you have questions, email, I'm coming. We send a time and meet, or we have a weekly meeting. Let's have a weekly meeting. Once the other student come and buy them, we sort the half an hour catch up every week. But you can also come and ask if you have something quickly. As I said, I'll dig more stuff, send them your way to start read about the topic. Main problem is we want to make sure less carry over so the steam go clean. Most focus now is, they can't do much about this, so they need to do other stuff. They wash the steam and they but if you improve the efficiency here, even if small fraction make a lot of difference. You
[0:18:03] Unknown Speaker(s): okay, okay, we're good. Thank you.
[0:18:13] Andy: Thank you. You i.
```

</details>

