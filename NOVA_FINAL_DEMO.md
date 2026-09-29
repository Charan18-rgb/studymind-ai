# StudyMind AI — Final 3-Minute Demo Script

**Target runtime: about 2 minutes 55 seconds.** Reset before the presentation and read the live result values from the app. The 42.0% → 53.0% (+11.0 points) example below is an observed run, not a guaranteed outcome. A different answer sequence may produce another result.

| Time | Presenter clicks / action | What should be visible | What to say |
|---|---|---|---|
| 0:00–0:20 | Start on **Dashboard**. Point to the Trees focus area and current Next Best Action. | Baseline learner state; Trees at 42%, Recursion at 51%; recommendation such as Review Recursion. | “StudyMind AI starts with a model of this learner. Trees is a weak area, and Recursion is also a prerequisite weakness.” |
| 0:20–0:40 | Click **Knowledge Map**. Select **Trees** if needed. | Trees detail, mastery, and prerequisite relationships. | “The graph gives the system context: Recursion points into Trees as a prerequisite. That lets it reason about a gap upstream of the target.” |
| 0:40–0:55 | Point to **Recursion → Trees**, then click **Practice Trees**. | The prerequisite edge and Trees concept drawer, then the practice session. | “I’ll practice Trees so we can see how the learner state changes.” |
| 0:55–1:20 | In **Adaptive Practice**, show the session context and answer the questions. | Target concept, live mastery and prerequisites, focus area, segmented question progress. Answer thoughtfully; do not repeat one choice mechanically. | “These questions are targeted to the weak concept, with the learner model’s prerequisite context visible.” |
| 1:20–1:50 | Complete the session and pause on **Session Results**. | Backend-returned score, before and after mastery, change, and updated next action. | “The server scores the answers and updates mastery. In one observed run, Trees moved from 42.0% to 53.0%, up 11.0 points. Your result may differ.” |
| 1:50–2:15 | Click **Back to Dashboard**. | Updated Trees state and recalculated Next Best Action. | “Now the recommendation is recalculated from the updated learner state. The next step can change after practice.” |
| 2:15–2:35 | Click **Reset Demo State** and wait for the page to reload its data. | Baseline mastery and baseline recommendation restored. | “Reset returns us to the same seeded demo state, ready for another run.” |
| 2:35–2:55 | Close on the Dashboard. | Baseline learner state and Next Best Action. | “StudyMind AI doesn't just explain the material. It understands the learner and decides what to learn next.” |

## Optional Ask My Notes cutaway

Skip this in the timed main story unless the judges ask. If shown, open **Materials**, ask one short question about the intended Data Structures PDF, and point to the cited source page. Retrieval ranks text chunks by token overlap/relevance; do not describe it as vector search.
