# Hackathon Demo Guide

Follow this step-by-step pipeline script to showcase **IndusMind AI**'s capabilities within 5 minutes.

---

## ⏱ 0:00 - 1:00 | System Architecture & Dashboard
1. Open the **Dashboard** at `http://localhost:5174/`.
2. Point out the **System Status Grid** showing green checkmarks for *FastAPI Server*, *ChromaDB Connection*, *Neo4j Database*, and *Google Gemini API*.
3. Highlight the **live statistics widgets**: total uploads, vector chunks, total graph nodes, and edges.

---

## ⏱ 1:00 - 2:00 | Ingestion & OCR Processing
1. Navigate to **Document Upload**.
2. Drag and drop `sample_manual.pdf` (or any scan).
3. Switch to **Processed Documents**. Point out the multi-stage status track showing lifecycle states: *PENDING* ➔ *PROCESSING* ➔ *EXTRACTED* ➔ *INDEXED*.
4. Click **View Details** to display the parsed UTF-8 text pane, extracted metadata attributes (char count, reading time), and individual chunk arrays.

---

## ⏱ 2:00 - 3:00 | Knowledge Graph Visualizer
1. Click **Build Knowledge Graph** on your uploaded document.
2. Go to the **Knowledge Graph** tab.
3. Show the interactive topology network built dynamically.
4. Filter nodes by entity types (Equipment, Procedure, safety warnings) and type in "Pump" to search matching component nodes.
5. Click a node to open the sidebar detail pane containing the chunk citations and extraction confidence levels.

---

## ⏱ 3:00 - 4:30 | AI Assistant Synthesis (LangGraph)
1. Go to the **AI Assistant** screen.
2. Select the suggested query: *"What is the recommended maintenance procedure for Pump P-101?"*
3. Send the message. Highlight the output response:
   - **Confidence Score**: High (e.g. 95%).
   - **Citations**: Direct link references to Chunk IDs.
   - **Reasoning Trace Accordion**: Open the LangGraph trace showing the sequence of agent execution steps (`Router` ➔ `SearchAgent` ➔ `GraphAgent` ➔ `KnowledgeAgent`).

---

## ⏱ 4:30 - 5:00 | Analytics & Wrap-up
1. Open the **Analytics** tab.
2. Point out the graphs mapping API request count spikes, average latency, and chunk distribution metrics.
3. Emphasize that all computations run on live data using a hybrid Vector + Graph semantic retrieval model.
