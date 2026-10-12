---
otter_id: "dXIVmcoEBj-CXnKmpIsbdo6hPaQ"
source_url: "https://otter.ai/u/dXIVmcoEBj-CXnKmpIsbdo6hPaQ"
source_start_time: "2026/03/18 18:05:11"
source_timezone: unspecified
imported_on: 2026-10-12
---

# Geothermal Separator - Week 3

| Field | Source value |
| --- | --- |
| Date and time | 2026/03/18 18:05:11 (timezone not supplied by connector) |
| Duration | 12m 47s |
| Source | [Otter recording](https://otter.ai/u/dXIVmcoEBj-CXnKmpIsbdo6hPaQ) |

Imported from Otter.ai. The summary and action items are Otter-generated; they record the meeting and are not verified project results. Original speaker labels and wording are retained. File dates use the timestamp supplied by Otter, without timezone conversion.

## Otter summary

The team discussed the efficiency of a separator in a geothermal system, focusing on producing dry steam to avoid turbine damage. They emphasized the importance of minimizing moisture content in the steam. The primary separator's efficiency was highlighted, with secondary mechanisms used if necessary. They plan to use CFD modeling to optimize the separator's performance. The team agreed to start with a simple homogeneous model, validate it with existing data, and then progress to a two-phase model. A literature review draft is expected by early April, with a detailed discussion scheduled for the next meeting.

## Otter action items

- Speaker 0 - : Review the posted student CFD model and provide feedback on what changes were made
- Speaker 1 - : Obtain field data for model validation (work on getting data from the field to support CFD validation)
- Speaker 3 - : Submit a 5–6 page draft literature review (research questions, objectives, scope) before next-week's meeting (deadline: next week Thursday) so supervisors can read and comment
- Speaker unknown - : Upload the latest CFD model files to the Teams channel so supervisors can review the changes

## Full transcript

<details>
<summary>Show the complete speaker-attributed transcript</summary>

```text
[0:00:03] Speaker 1: Yeah, so what do we have today? So I guess you said we just bring up questions and try, try, get, I guess, a little bit more general idea for things. And after reading, yeah, I haven't read the entire all of the papers that you've sent me, but what you sent us? But yeah, I guess we have little questions. I guess we don't have like, full, like deep understanding here, so we might not have the best questions yet. But yeah, that's really fine. Just, you're sort of just finding your way, yeah, yes. So I guess I'll start with one of the questions. So, like, when the fluids go into the separator, right? So obviously, there's a lot of components before the separator. What should we expect? Like, what, what elements should we be expecting? Like, make assumptions on, like, the most common things that go into the food, like the separator or, like, is it specific to, like, a geothermal site? Yeah, but it could be. Is it different, like, like, some minerals could be different to, like, a specific,
[0:01:21] Speaker 2: like, geothermal fuel. It can be different. Each field has its own signature, but we don't care about that. Okay, we are looking at efficiency of the separator. The separator need to produce dry steam. That dry steam will drive the turbine that generate electricity, any small droplets and moisture would that damage the turbine? Yeah, they carry, they carry the mineral from the water, and they erode the turbine.
[0:01:51] Andy: Okay, yeah, so the makeup of the mineral doesn't really affect the how the it doesn't. Okay.
[0:02:00] Speaker 2: Around. So this is a turbine blade for your information. When it
[0:02:10] Unknown Speaker(s): turns like, like a propeller, basically, and the moisture comes and all this cuts
[0:02:18] Speaker 2: all of this or damage this, because they travel at high velocity, they become like bullets in the steam and damages and then reduce the efficiency and the life of the turbine. So we want the steam to be as dry as possible. And the main component that separates steam from water is the separator, the big side. Separated the excitement.
[0:02:53] Andy: So, I mean, you got there was like a couple papers in here that actually talks about what happens after the separator?
[0:03:04] Speaker 2: So, because the separator is not efficient, we try to reduce the number of the amount of moisture downstream with other mechanisms but the mean. So we call it primary separator. This is secondary separation. If the primary separator is efficient, you lose you have less problems, less need for the rest.
[0:03:31] Speaker 1: Okay, so we don't, we don't care. We don't care too much about what happens after. We just want to make it as
[0:03:37] Speaker 2: efficient as possible. CFD, just for the separator. We wanted to make it as efficient as possible. Not many water droplets coming up. And with the CFD, you will be seeing what comes out, because when you model it as two phase going in, you can see there are droplets, because there's still two phases going, and that's what we want to see. And what can we do to once we have a model running, what would we do to reduce the moisture coming up?
[0:04:21] Andy: So for like, say, after we get it running, are we gonna able to, like, validate it against measured data?
[0:04:38] Speaker 2: I can work. I'm working on getting some data on the field, but some that one of the paper has some information, some data already
[0:04:51] Speaker 3: there you can, you can validate with that paper, right? Yeah, doesn't mean that for validation. You can only validate with current experimental data, if you can validate with the existing, published data, that's enough for the project. Yeah. Have you had a chance to read last year students report?
[0:05:17] Speaker 1: I've only really, I've only looked up like the first couple of pages. So not, not in depth.
[0:05:25] Speaker 2: So, I mean, you can validate one of validation you compare CFD model with CFD model. The CFD model that you have now is basically homogeneous, and this one has, we're going to start with two phase from the beginning. So compare this with this, because it's a different modeling approach,
[0:05:51] Speaker 3: and also there are some analytical formulation that you can value, you can validate with that, but you need to do some simplification if you want divided with analytical so you open answers,
[0:06:12] Unknown Speaker(s): or no, you open the fourth model I've looked at it. Let's put the model
[0:06:18] Speaker 3: into the teams channel as well the latest one, and then I can look at your model, what sort of changes you made. Yeah,
[0:06:29] Speaker 2: okay, yeah. As I said, there are three different models we can focus on one the best design, yeah, the spiral inlet. They call the other ones. Which one they have put the model in. So when is the time for literature? Next week. Next next week?
[0:06:56] Speaker 3: Thursday. So do you do you want to send us a draft, just a draft of the literature review or project is called, then we can put the comment
[0:07:08] Andy: before that. Yes, really good. I mean, just like conceptually for this, for the CFD part, I think the main like improvement, or like, whatever that we're going to do now is how we model the fluid coming in, right? Like, instead of, say, homogeneous, we actually model it as, like a two phase, like, model it as is, I would suggest at the beginning,
[0:07:35] Speaker 3: maybe just initial model, just consider as a homogeneous running to see if you're comfortable with the CFD, all the parameters that for how you can change the fluid parameters, how you can change the velocity, how you can just run it as soon as possible as a homogeneous Yeah. And then once you're comfortable with your model, then we can go one step further in advance, then change to the two phase, don't I mean, don't start with a very complex model in the final element, start as simple as possible, and step by step at complexities absolutely
[0:08:18] Speaker 2: makes sense. So just run and get comfortable
[0:08:25] Speaker 1: and But that's after the literature review, right? What should we start getting
[0:08:29] Speaker 3: right now? Just keep reading. Yeah, and we expect the first months to April, 1 week of April, a student are no you know, they know about the project. They know about the research questions and scope of the project. And once you submit the literature review, the next step to run very simple CFD model, come to the meeting with question about CFD, and then a step by step, change the parameters you it
[0:09:07] Unknown Speaker(s): makes sense.
[0:09:14] Speaker 1: And with like, the complexity of the model, it can be like. So obviously, we start from like something simple. And as we get more familiar with the software, we add complexity to it. Is there like, like, can we go if we have time, obviously, do we just keep on adding like complexity and try and make it better? Or like, is it like, a certain point that we should just,
[0:09:37] Speaker 2: like, Well, okay, just get started. Yeah. And then slowly we can, but
[0:09:44] Speaker 3: goal is to model two phase, right? You can add more complexity on that. Can consider, for example, turbulent or so, but the right now, the goal is model two phase in the CFD in 344, you just know the one phase, and you it was air, right? A very simple case, right? Not even fluid. Fluid. I mean, water isn't, is complex than air. Yeah, you guys started with air. And then, for example, in then, you know, your first CFD, maybe you can just consider, I mean, water, something, not, not, not air, you know, fluid, not the gas. And the next step, at, for example, fluid and air. And the next step, Steam, you know, and water you know, make sense, since you have the last year model, I think your job is quite straightforward. You don't need to design it. You have your own cat file, I mean, your previous last year CFD. You at least know about the geometry. You know about the boundary conditions. Now your work is quite straightforward. I think there is not too much preparation or creating geometry, or, you know, defining the boundary conditions. Everything is quite handy in your hand. You so for the next week, please, before the meeting, send us the draft of the literature review, and then we can discuss about the literature review in the meeting. This is and write the researchers. Go research. What's your research question? What is the objective of this? And then literature review send us a drug before the meeting, and then we can have time, for example, two, three hours, to read it. And then in the meeting, we can discuss about that. And we need for the
[0:11:59] Speaker 1: submime might be a little bit last minute, because I do have tests next week, Wednesday. Okay, yeah, hopefully I will get it done in time. But yeah.
[0:12:14] Andy: So when do you so? What if I send it on Wednesday, would that be too late for you to review it?
[0:12:26] Speaker 3: Okay, just five, six pages, right? Just, yeah, for me, it's just the one hour to read.
[0:12:34] Unknown Speaker(s): Okay, cool. Okay, yeah, more questions. More questions. No more. Next time, yeah, hopefully bye.
```

</details>

