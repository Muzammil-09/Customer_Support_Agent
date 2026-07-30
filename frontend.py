# """
# Simple chat frontend for the FMG AI Customer Support backend.

# This file has NO dependency on your main script - it just exposes a
# `run_frontend(answer_fn)` function. Your main script imports this file and
# passes it `answer_customer_question` (the function itself, not a call to
# it), which avoids any circular import between the two files.

# Install:
#     pip install flask
# """

# from flask import Flask, request, jsonify, render_template_string

# app = Flask(__name__)

# # Set by run_frontend() / init_frontend() at startup - this is how the
# # frontend calls back into your main.py's answer_customer_question without
# # main.py and frontend.py importing each other.
# _answer_fn = None


# HTML_PAGE = """
# <!DOCTYPE html>
# <html lang="en">
# <head>
# <meta charset="UTF-8" />
# <title>FMG AI Customer Support</title>
# <style>
#   * { box-sizing: border-box; }
#   body {
#     font-family: -apple-system, Segoe UI, Roboto, Arial, sans-serif;
#     background: #f4f5f7;
#     margin: 0;
#     display: flex;
#     justify-content: center;
#     padding: 24px;
#   }
#   #app {
#     width: 100%;
#     max-width: 720px;
#     background: #fff;
#     border-radius: 12px;
#     box-shadow: 0 2px 10px rgba(0,0,0,0.08);
#     display: flex;
#     flex-direction: column;
#     height: 85vh;
#     overflow: hidden;
#   }
#   header {
#     padding: 16px 20px;
#     background: #1a2a4a;
#     color: #fff;
#     font-weight: 600;
#     font-size: 16px;
#   }
#   #messages {
#     flex: 1;
#     overflow-y: auto;
#     padding: 20px;
#     display: flex;
#     flex-direction: column;
#     gap: 14px;
#   }
#   .msg {
#     max-width: 85%;
#     padding: 10px 14px;
#     border-radius: 10px;
#     white-space: pre-wrap;
#     line-height: 1.45;
#     font-size: 14px;
#   }
#   .user {
#     align-self: flex-end;
#     background: #1a2a4a;
#     color: #fff;
#     border-bottom-right-radius: 2px;
#   }
#   .bot {
#     align-self: flex-start;
#     background: #eef0f4;
#     color: #1a1a1a;
#     border-bottom-left-radius: 2px;
#   }
#   .bot.loading { color: #888; font-style: italic; }
#   form {
#     display: flex;
#     border-top: 1px solid #eee;
#     padding: 12px;
#     gap: 8px;
#   }
#   input[type=text] {
#     flex: 1;
#     padding: 10px 12px;
#     border: 1px solid #ddd;
#     border-radius: 8px;
#     font-size: 14px;
#   }
#   button {
#     padding: 10px 18px;
#     background: #1a2a4a;
#     color: #fff;
#     border: none;
#     border-radius: 8px;
#     cursor: pointer;
#     font-size: 14px;
#   }
#   button:disabled { opacity: 0.6; cursor: default; }
# </style>
# </head>
# <body>
#   <div id="app">
#     <header>FMG AI Customer Support</header>
#     <div id="messages"></div>
#     <form id="chat-form">
#       <input type="text" id="question" placeholder="Type your question..." autocomplete="off" />
#       <button type="submit" id="send-btn">Send</button>
#     </form>
#   </div>

# <script>
# const messagesEl = document.getElementById('messages');
# const formEl = document.getElementById('chat-form');
# const inputEl = document.getElementById('question');
# const sendBtn = document.getElementById('send-btn');

# function addMessage(text, sender) {
#   const div = document.createElement('div');
#   div.className = 'msg ' + sender;
#   div.textContent = text;
#   messagesEl.appendChild(div);
#   messagesEl.scrollTop = messagesEl.scrollHeight;
#   return div;
# }

# formEl.addEventListener('submit', async (e) => {
#   e.preventDefault();
#   const question = inputEl.value.trim();
#   if (!question) return;

#   addMessage(question, 'user');
#   inputEl.value = '';
#   sendBtn.disabled = true;

#   const loadingEl = addMessage('Thinking...', 'bot loading');

#   try {
#     const res = await fetch('/ask', {
#       method: 'POST',
#       headers: { 'Content-Type': 'application/json' },
#       body: JSON.stringify({ question })
#     });
#     const data = await res.json();
#     loadingEl.remove();
#     addMessage(data.answer || 'No response received.', 'bot');
#   } catch (err) {
#     loadingEl.remove();
#     addMessage('Error contacting the server: ' + err, 'bot');
#   } finally {
#     sendBtn.disabled = false;
#     inputEl.focus();
#   }
# });
# </script>
# </body>
# </html>
# """


# @app.route("/")
# def index():
#     return render_template_string(HTML_PAGE)


# @app.route("/ask", methods=["POST"])
# def ask():
#     data = request.get_json(silent=True) or {}
#     question = (data.get("question") or "").strip()

#     if not question:
#         return jsonify({"answer": "Please enter a question."})

#     if _answer_fn is None:
#         return jsonify({"answer": "Backend is not initialized."}), 500

#     try:
#         answer = _answer_fn(question)
#     except Exception as e:
#         answer = f"Something went wrong while generating a response: {e}"

#     return jsonify({"answer": answer})


# def init_frontend(answer_fn):
#     """Registers the backend function the frontend should call for each
#     question. Call this (or use run_frontend below) before serving."""
#     global _answer_fn
#     _answer_fn = answer_fn
#     return app


# def run_frontend(answer_fn, host="127.0.0.1", port=5000, debug=False):
#     """Convenience one-liner: registers the backend function and starts
#     the Flask server. Call this from your main.py's __main__ block."""
#     init_frontend(answer_fn)
#     print(f"\nFMG AI Customer Support is running at: http://{host}:{port}\n")
#     app.run(host=host, port=port, debug=debug)


# if __name__ == "__main__":
#     # Lets you sanity-check the UI on its own with a dummy backend, without
#     # needing your real main.py / Groq key / vector store wired up yet.
#     run_frontend(lambda q: f"(demo mode) You asked: {q}")

"""
Chat frontend for the FMG AI Customer Support agent (main.py).

This file has NO dependency on your main script - it just exposes a
`run_frontend(answer_fn)` function. main.py imports this file and passes
it `answer_customer_question` (the function itself, not a call to it),
which avoids any circular import between the two files.

answer_customer_question() returns ONE string that looks like:

    <answer text>

    Sources:
    - FMG Documentation: user-guide.pdf, page 12
    - Previous Support Ticket: KAN-1

    Draft Ticket Reply:
    <agent-ready reply text>

("Sources:" is omitted when escalate=True, since there are none.)
This frontend splits that string on the same "\\n\\nSources:\\n" /
"\\n\\nDraft Ticket Reply:\\n" markers your backend writes, so each part
renders as its own labeled block instead of one undifferentiated blob.

Install:
    pip install flask
"""

from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

# Set by run_frontend() / init_frontend() at startup - this is how the
# frontend calls back into your main.py's answer_customer_question without
# main.py and frontend.py importing each other.
_answer_fn = None

# Must match the separators your backend's _format_citations() /
# _format_draft_reply() helpers use, so the frontend can split the
# returned string back into its three parts.
SOURCES_MARKER = "\n\nSources:\n"
DRAFT_REPLY_MARKER = "\n\nDraft Ticket Reply:\n"


HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<title>FMG AI Customer Support</title>
<style>
  * { box-sizing: border-box; }
  body {
    font-family: -apple-system, Segoe UI, Roboto, Arial, sans-serif;
    background: #f0f2f6;
    margin: 0;
    display: flex;
    justify-content: center;
    padding: 24px;
  }
  #app {
    width: 100%;
    max-width: 760px;
    background: #fff;
    border-radius: 12px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.08);
    display: flex;
    flex-direction: column;
    height: 88vh;
    overflow: hidden;
  }
  header {
    padding: 16px 20px;
    background: #10213f;
    color: #fff;
  }
  header .title { font-weight: 700; font-size: 17px; }
  header .subtitle { font-size: 12px; color: #9fb0cc; margin-top: 2px; }

  #messages {
    flex: 1;
    overflow-y: auto;
    padding: 20px;
    display: flex;
    flex-direction: column;
    gap: 16px;
  }

  .row { display: flex; }
  .row.user { justify-content: flex-end; }
  .row.bot { justify-content: flex-start; }

  .bubble {
    max-width: 88%;
    padding: 12px 15px;
    border-radius: 12px;
    white-space: pre-wrap;
    line-height: 1.5;
    font-size: 14.5px;
  }
  .user .bubble { background: #10213f; color: #fff; border-bottom-right-radius: 3px; }
  .bot .bubble { background: #eef1f6; color: #1a1a1a; border-bottom-left-radius: 3px; }
  .bot .bubble.loading { color: #888; font-style: italic; }

  .bot-wrap { display: flex; flex-direction: column; gap: 8px; max-width: 88%; }

  .card {
    border: 1px solid #e2e6ee;
    border-radius: 10px;
    overflow: hidden;
    background: #fff;
  }
  .card-header {
    padding: 8px 12px;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 0.03em;
    text-transform: uppercase;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  .card-body {
    padding: 10px 12px;
    font-size: 13.5px;
    white-space: pre-wrap;
    line-height: 1.5;
  }

  .card.sources .card-header { background: #eaf3ea; color: #1e5e2b; }
  .card.sources .card-body { color: #234; }
  .card.sources ul { margin: 0; padding-left: 18px; }
  .card.sources li { margin-bottom: 4px; }

  .card.draft .card-header { background: #eef1fb; color: #263b9c; }
  .card.draft .card-body { color: #222; background: #fbfbfd; }

  .copy-btn {
    border: none;
    background: #263b9c;
    color: #fff;
    font-size: 11px;
    padding: 3px 9px;
    border-radius: 6px;
    cursor: pointer;
  }
  .copy-btn:active { transform: scale(0.97); }

  form {
    display: flex;
    border-top: 1px solid #eee;
    padding: 12px;
    gap: 8px;
  }
  input[type=text] {
    flex: 1;
    padding: 10px 12px;
    border: 1px solid #ddd;
    border-radius: 8px;
    font-size: 14px;
  }
  button.send {
    padding: 10px 18px;
    background: #10213f;
    color: #fff;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    font-size: 14px;
  }
  button.send:disabled { opacity: 0.6; cursor: default; }
</style>
</head>
<body>
  <div id="app">
    <header>
      <div class="title">FMG AI Customer Support</div>
      <div class="subtitle">Answers grounded in FMG documentation &amp; past support tickets</div>
    </header>
    <div id="messages"></div>
    <form id="chat-form">
      <input type="text" id="question" placeholder="Type your question..." autocomplete="off" />
      <button type="submit" class="send" id="send-btn">Send</button>
    </form>
  </div>

<script>
const messagesEl = document.getElementById('messages');
const formEl = document.getElementById('chat-form');
const inputEl = document.getElementById('question');
const sendBtn = document.getElementById('send-btn');

const SOURCES_MARKER = "\\n\\nSources:\\n";
const DRAFT_REPLY_MARKER = "\\n\\nDraft Ticket Reply:\\n";

function addUserMessage(text) {
  const row = document.createElement('div');
  row.className = 'row user';
  row.innerHTML = '<div class="bubble"></div>';
  row.querySelector('.bubble').textContent = text;
  messagesEl.appendChild(row);
  messagesEl.scrollTop = messagesEl.scrollHeight;
  return row;
}

function addLoadingMessage() {
  const row = document.createElement('div');
  row.className = 'row bot';
  row.innerHTML = '<div class="bubble loading">Thinking...</div>';
  messagesEl.appendChild(row);
  messagesEl.scrollTop = messagesEl.scrollHeight;
  return row;
}

// Splits the backend's single string into { answer, sources, draftReply }
// using the same markers the backend writes them with.
function parseResponse(raw) {
  let answer = raw;
  let sources = null;
  let draftReply = null;

  const draftIdx = answer.indexOf(DRAFT_REPLY_MARKER);
  if (draftIdx !== -1) {
    draftReply = answer.slice(draftIdx + DRAFT_REPLY_MARKER.length).trim();
    answer = answer.slice(0, draftIdx);
  }

  const sourcesIdx = answer.indexOf(SOURCES_MARKER);
  if (sourcesIdx !== -1) {
    sources = answer.slice(sourcesIdx + SOURCES_MARKER.length).trim();
    answer = answer.slice(0, sourcesIdx);
  }

  return { answer: answer.trim(), sources, draftReply };
}

function renderBotResponse(raw) {
  const { answer, sources, draftReply } = parseResponse(raw);

  const wrap = document.createElement('div');
  wrap.className = 'bot-wrap';

  const answerBubble = document.createElement('div');
  answerBubble.className = 'bubble';
  answerBubble.textContent = answer || '(No answer text returned.)';
  wrap.appendChild(answerBubble);

  if (sources) {
    const card = document.createElement('div');
    card.className = 'card sources';
    const lines = sources.split('\\n').filter(l => l.trim().length > 0);
    const items = lines.map(l => '<li>' + l.replace(/^-\\s*/, '') + '</li>').join('');
    card.innerHTML =
      '<div class="card-header"><span>Sources</span></div>' +
      '<div class="card-body"><ul>' + items + '</ul></div>';
    wrap.appendChild(card);
  }

  if (draftReply) {
    const card = document.createElement('div');
    card.className = 'card draft';
    card.innerHTML =
      '<div class="card-header"><span>Draft Ticket Reply</span>' +
      '<button class="copy-btn" type="button">Copy</button></div>' +
      '<div class="card-body"></div>';
    card.querySelector('.card-body').textContent = draftReply;
    card.querySelector('.copy-btn').addEventListener('click', () => {
      navigator.clipboard.writeText(draftReply);
      const btn = card.querySelector('.copy-btn');
      const original = btn.textContent;
      btn.textContent = 'Copied';
      setTimeout(() => { btn.textContent = original; }, 1200);
    });
    wrap.appendChild(card);
  }

  const row = document.createElement('div');
  row.className = 'row bot';
  row.appendChild(wrap);
  messagesEl.appendChild(row);
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

formEl.addEventListener('submit', async (e) => {
  e.preventDefault();
  const question = inputEl.value.trim();
  if (!question) return;

  addUserMessage(question);
  inputEl.value = '';
  sendBtn.disabled = true;

  const loadingRow = addLoadingMessage();

  try {
    const res = await fetch('/ask', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question })
    });
    const data = await res.json();
    loadingRow.remove();
    renderBotResponse(data.answer || 'No response received.');
  } catch (err) {
    loadingRow.remove();
    const row = document.createElement('div');
    row.className = 'row bot';
    row.innerHTML = '<div class="bubble">Error contacting the server: ' + err + '</div>';
    messagesEl.appendChild(row);
  } finally {
    sendBtn.disabled = false;
    inputEl.focus();
  }
});
</script>
</body>
</html>
"""


@app.route("/")
def index():
    return render_template_string(HTML_PAGE)


@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json(silent=True) or {}
    question = (data.get("question") or "").strip()

    if not question:
        return jsonify({"answer": "Please enter a question."})

    if _answer_fn is None:
        return jsonify({"answer": "Backend is not initialized."}), 500

    try:
        answer = _answer_fn(question)
    except Exception as e:
        answer = f"Something went wrong while generating a response: {e}"

    return jsonify({"answer": answer})


def init_frontend(answer_fn):
    """Registers the backend function (answer_customer_question) the
    frontend should call for each question. Call this, or use
    run_frontend below, before serving."""
    global _answer_fn
    _answer_fn = answer_fn
    return app


def run_frontend(answer_fn, host="127.0.0.1", port=5000, debug=False):
    """Convenience one-liner: registers the backend function and starts
    the Flask server. Call this from main.py's __main__ block:

        if __name__ == "__main__":
            run_frontend(answer_customer_question)
    """
    init_frontend(answer_fn)
    print(f"\nFMG AI Customer Support is running at: http://{host}:{port}\n")
    app.run(host=host, port=port, debug=debug)


if __name__ == "__main__":
    # Lets you sanity-check the UI on its own, with a fake backend that
    # mimics your real answer_customer_question's output format - useful
    # for checking the Sources/Draft Reply cards render correctly before
    # wiring up the real Groq/vector-store backend.
    def _demo_answer(question):
        return (
            f"Here's how to handle that: {question}\n\n"
            "Sources:\n"
            "- FMG Documentation: user-guide.pdf, page 12\n"
            "- Previous Support Ticket: KAN-1\n\n"
            "Draft Ticket Reply:\n"
            "Hi there,\n\nThanks for reaching out! Here's how to resolve this...\n\nBest,\nFMG Support"
        )

    run_frontend(_demo_answer)