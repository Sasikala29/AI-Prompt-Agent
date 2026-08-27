
const API_BASE = "";

let currentConversationId = null;
const currentUserId = 1;

/* ============================================================
   MAIN CHAT ELEMENTS
============================================================ */

const messagesEl = document.getElementById("messages");
const conversationListEl = document.getElementById("conversationList");
const chatForm = document.getElementById("chatForm");
const messageInput = document.getElementById("message");
const sendButton = document.getElementById("sendButton");
const newChatButton = document.getElementById("newChatButton");

const modelSelect = document.getElementById("model");
const modeSelect = document.getElementById("mode");
const techniqueSelect = document.getElementById("technique");

const temperatureInput = document.getElementById("temperature");
const temperatureValue = document.getElementById("temperatureValue");

const topPInput = document.getElementById("topP");
const topPValue = document.getElementById("topPValue");

const maxTokensInput = document.getElementById("maxTokens");
const responseFormatSelect = document.getElementById("responseFormat");

/* ============================================================
   PROMPT TECHNIQUE FIELDS
============================================================ */

const roleField = document.getElementById("roleField");
const contextField = document.getElementById("contextField");
const constraintsField = document.getElementById("constraintsField");
const expectedOutputField = document.getElementById("expectedOutputField");
const examplesField = document.getElementById("examplesField");

const roleInput = document.getElementById("role");
const contextInput = document.getElementById("context");
const constraintsInput = document.getElementById("constraints");
const expectedOutputInput = document.getElementById("expectedOutput");
const examplesInput = document.getElementById("examples");

/* ============================================================
   DATABASE VIEWER
============================================================ */

const databaseButton = document.getElementById("databaseButton");
const databaseView = document.getElementById("databaseView");
const chatView = document.getElementById("chatView");
const databaseContent = document.getElementById("databaseContent");
const refreshDatabase = document.getElementById("refreshDatabase");
const pageTitle = document.getElementById("pageTitle");
const databaseTabs = document.querySelectorAll(".db-tab");

let currentDatabaseTable = "users";

/* ============================================================
   PROMPT COMPARISON
============================================================ */

const comparisonView = document.getElementById("comparisonView");
const comparisonTask = document.getElementById("comparisonTask");
const comparisonTechnique1 = document.getElementById("comparisonTechnique1");
const comparisonTechnique2 = document.getElementById("comparisonTechnique2");
const comparisonRole = document.getElementById("comparisonRole");
const comparisonExpected = document.getElementById("comparisonExpected");
const comparisonContext = document.getElementById("comparisonContext");
const comparisonConstraints = document.getElementById("comparisonConstraints");
const compareButton = document.getElementById("compareButton");
const comparisonResults = document.getElementById("comparisonResults");
const comparisonLoading = document.getElementById("comparisonLoading");
const backToChat = document.getElementById("backToChat");
const comparisonButton = document.getElementById("comparisonButton");

/* ============================================================
   INITIALIZATION
============================================================ */

document.addEventListener("DOMContentLoaded", async () => {
    updateTechniqueFields();

    if (temperatureInput && temperatureValue) {
        temperatureValue.textContent = temperatureInput.value;

        temperatureInput.addEventListener("input", () => {
            temperatureValue.textContent = temperatureInput.value;
        });
    }

    if (topPInput && topPValue) {
        topPValue.textContent = topPInput.value;

        topPInput.addEventListener("input", () => {
            topPValue.textContent = topPInput.value;
        });
    }

    await loadConversations();
});

/* ============================================================
   NEW CHAT
============================================================ */

if (newChatButton) {
    newChatButton.addEventListener("click", () => {
        currentConversationId = null;

        if (databaseView) {
            databaseView.classList.add("hidden");
        }

        if (comparisonView) {
            comparisonView.classList.add("hidden");
        }

        if (chatView) {
            chatView.classList.remove("hidden");
        }

        if (pageTitle) {
            pageTitle.textContent = "AI Assistant";
        }

        messagesEl.innerHTML = `
            <div class="welcome">
                <h2>How can I help?</h2>
                <p>
                    Create, improve, compare prompts,
                    use tools, or ask a normal question.
                </p>
            </div>
        `;

        messageInput.focus();
    });
}

/* ============================================================
   PROMPT TECHNIQUE DROPDOWN
============================================================ */

if (techniqueSelect) {
    techniqueSelect.addEventListener("change", updateTechniqueFields);
}

function updateTechniqueFields() {
    if (!techniqueSelect) {
        return;
    }

    const technique = techniqueSelect.value;

    hideAllTechniqueFields();

    /*
     * ZERO-SHOT
     * No examples are required.
     */

    if (technique === "zero-shot") {
        return;
    }

    /*
     * ONE-SHOT
     * Exactly one example can be supplied.
     */

    if (technique === "one-shot") {
        if (examplesField) {
            examplesField.classList.remove("hidden");
        }
        return;
    }

    /*
     * FEW-SHOT
     * Multiple examples can be supplied.
     */

    if (technique === "few-shot") {
        if (examplesField) {
            examplesField.classList.remove("hidden");
        }
        return;
    }

    /*
     * ROLE-BASED
     */

    if (technique === "role-based") {
        if (roleField) {
            roleField.classList.remove("hidden");
        }
        return;
    }

    /*
     * CHAIN-OF-THOUGHT
     *
     * No example is required.
     * We allow context and constraints.
     */

    if (technique === "chain-of-thought") {
        if (contextField) {
            contextField.classList.remove("hidden");
        }

        if (constraintsField) {
            constraintsField.classList.remove("hidden");
        }

        if (expectedOutputField) {
            expectedOutputField.classList.remove("hidden");
        }

        return;
    }

    /*
     * STRUCTURED
     */

    if (technique === "structured") {
        if (roleField) {
            roleField.classList.remove("hidden");
        }

        if (contextField) {
            contextField.classList.remove("hidden");
        }

        if (constraintsField) {
            constraintsField.classList.remove("hidden");
        }

        if (expectedOutputField) {
            expectedOutputField.classList.remove("hidden");
        }

        return;
    }
}

function hideAllTechniqueFields() {
    if (roleField) {
        roleField.classList.add("hidden");
    }

    if (contextField) {
        contextField.classList.add("hidden");
    }

    if (constraintsField) {
        constraintsField.classList.add("hidden");
    }

    if (expectedOutputField) {
        expectedOutputField.classList.add("hidden");
    }

    if (examplesField) {
        examplesField.classList.add("hidden");
    }
}

/* ============================================================
   EXAMPLES PARSER
============================================================ */

/*
 * IMPORTANT:
 *
 * Backend agent schema expects:
 *
 * examples: Optional[str]
 *
 * Therefore this function returns a STRING.
 *
 * Do NOT send an array here.
 *
 * Supported input formats:
 *
 * Input: I am happy
 * Output: Positive
 *
 * Input: I am angry
 * Output: Negative
 *
 * Also supports:
 *
 * Input: ...
 * Expected Output: ...
 *
 * And:
 *
 * Example 1:
 * Input: ...
 * Output: ...
 *
 * Example 2:
 * Input: ...
 * Output: ...
 */

function parseExamplesForBackend(rawExamples, technique) {
    if (!rawExamples) {
        return null;
    }

    let text = String(rawExamples)
        .replace(/\r\n/g, "\n")
        .replace(/\r/g, "\n")
        .trim();

    if (!text) {
        return null;
    }

    /*
     * Normalize "Expected Output:" to "Output:"
     */

    text = text.replace(
        /^\s*Expected\s+Output\s*:/gim,
        "Output:"
    );

    /*
     * Normalize "Input :" and "Output :"
     */

    text = text.replace(
        /^\s*Input\s*:/gim,
        "Input:"
    );

    text = text.replace(
        /^\s*Output\s*:/gim,
        "Output:"
    );

    /*
     * Remove empty lines at the beginning/end.
     */

    text = text.trim();

    /*
     * Split examples.
     *
     * The backend parser already understands blocks
     * separated by blank lines.
     */

    const blocks = text
        .split(/\n\s*\n+/)
        .map(block => block.trim())
        .filter(Boolean);

    /*
     * ONE-SHOT
     *
     * Keep only one example.
     */

    if (technique === "one-shot") {
        if (blocks.length > 0) {
            return blocks[0];
        }

        return text;
    }

    /*
     * FEW-SHOT
     *
     * Keep all examples.
     */

    if (technique === "few-shot") {
        return blocks.join("\n\n");
    }

    /*
     * For other techniques, examples are normally
     * not required. If supplied, preserve them.
     */

    return blocks.join("\n\n");
}

/* ============================================================
   VALIDATE PROMPT TECHNIQUE
============================================================ */

function validateTechniqueInput(technique) {
    const examples = examplesInput
        ? examplesInput.value.trim()
        : "";

    /*
     * ONE-SHOT
     */

    if (technique === "one-shot") {
        if (!examples) {
            return {
                valid: false,
                message:
                    "One-shot prompting requires exactly one example. Please enter an example."
            };
        }

        const parsedExamples =
            parseExamplesForBackend(
                examples,
                technique
            );

        if (!parsedExamples) {
            return {
                valid: false,
                message:
                    "Please provide one valid example using Input: and Output:."
            };
        }
    }

    /*
     * FEW-SHOT
     */

    if (technique === "few-shot") {
        if (!examples) {
            return {
                valid: false,
                message:
                    "Few-shot prompting requires at least two examples."
            };
        }

        const blocks = examples
            .replace(/\r\n/g, "\n")
            .split(/\n\s*\n+/)
            .map(block => block.trim())
            .filter(Boolean);

        if (blocks.length < 2) {
            return {
                valid: false,
                message:
                    "Few-shot prompting requires at least two examples separated by a blank line."
            };
        }
    }

    return {
        valid: true
    };
}

/* ============================================================
   ERROR MESSAGE HANDLER
============================================================ */

function getErrorMessage(data, fallback) {
    if (!data) {
        return fallback;
    }

    if (typeof data.detail === "string") {
        return data.detail;
    }

    if (Array.isArray(data.detail)) {
        return data.detail
            .map(item => {
                if (typeof item === "string") {
                    return item;
                }

                if (item.msg) {
                    const location =
                        Array.isArray(item.loc)
                            ? item.loc.join(" → ")
                            : "";

                    return location
                        ? `${location}: ${item.msg}`
                        : item.msg;
                }

                return JSON.stringify(item);
            })
            .join("\n");
    }

    if (
        data.detail &&
        typeof data.detail === "object"
    ) {
        if (data.detail.message) {
            return String(data.detail.message);
        }

        if (data.detail.error) {
            return String(data.detail.error);
        }

        if (data.detail.detail) {
            return String(data.detail.detail);
        }

        try {
            return JSON.stringify(data.detail);
        } catch {
            return fallback;
        }
    }

    if (typeof data.error === "string") {
        return data.error;
    }

    if (typeof data.message === "string") {
        return data.message;
    }

    return fallback;
}

/* ============================================================
   BUILD CHAT REQUEST
============================================================ */

function buildChatRequest(message) {
    const technique = techniqueSelect
        ? techniqueSelect.value
        : "zero-shot";

    const rawExamples = examplesInput
        ? examplesInput.value.trim()
        : "";

    /*
     * Convert examples to the STRING expected
     * by /api/agent/chat.
     */

    const parsedExamples =
        parseExamplesForBackend(
            rawExamples,
            technique
        );

    return {
        message: message,

        conversation_id:
            currentConversationId,

        user_id:
            currentUserId,

        model:
            modelSelect
                ? modelSelect.value
                : "mistral",

        temperature:
            temperatureInput
                ? Number(temperatureInput.value)
                : 0.7,

        top_p:
            topPInput
                ? Number(topPInput.value)
                : 0.9,

        max_tokens:
            maxTokensInput
                ? Number(maxTokensInput.value)
                : 512,

        response_format:
            responseFormatSelect
                ? responseFormatSelect.value
                : "text",

        technique: technique,

        role:
            roleInput &&
            roleInput.value.trim()
                ? roleInput.value.trim()
                : null,

        context:
            contextInput &&
            contextInput.value.trim()
                ? contextInput.value.trim()
                : null,

        constraints:
            constraintsInput &&
            constraintsInput.value.trim()
                ? constraintsInput.value.trim()
                : null,

        expected_output:
            expectedOutputInput &&
            expectedOutputInput.value.trim()
                ? expectedOutputInput.value.trim()
                : null,

        /*
         * IMPORTANT:
         *
         * examples is STRING, not ARRAY.
         */

        examples:
            parsedExamples
    };
}

/* ============================================================
   CHAT SUBMIT
============================================================ */

if (chatForm) {
    chatForm.addEventListener(
        "submit",
        async event => {
            event.preventDefault();

            const message =
                messageInput.value.trim();

            if (!message) {
                return;
            }

            const technique =
                techniqueSelect
                    ? techniqueSelect.value
                    : "zero-shot";

            /*
             * Validate technique-specific input
             * before calling backend.
             */

            const validation =
                validateTechniqueInput(
                    technique
                );

            if (!validation.valid) {
                appendMessage(
                    "assistant",
                    `Error: ${validation.message}`
                );

                return;
            }

            appendMessage(
                "user",
                message
            );

            messageInput.value = "";

            sendButton.disabled = true;
            messageInput.disabled = true;

            const loading =
                appendMessage(
                    "assistant",
                    "Thinking..."
                );

            try {
                const requestBody =
                    buildChatRequest(
                        message
                    );

                /*
                 * ====================================================
                 * AGENT MODE
                 * ====================================================
                 */

                if (
                    modeSelect &&
                    modeSelect.value === "agent"
                ) {
                    const response =
                        await fetch(
                            `${API_BASE}/api/agent/chat`,
                            {
                                method: "POST",
                                headers: {
                                    "Content-Type":
                                        "application/json"
                                },
                                body:
                                    JSON.stringify(
                                        requestBody
                                    )
                            }
                        );

                    let data;

                    try {
                        data =
                            await response.json();
                    } catch {
                        throw new Error(
                            `Server returned HTTP ${response.status}`
                        );
                    }

                    if (!response.ok) {
                        throw new Error(
                            getErrorMessage(
                                data,
                                "Unable to get a response."
                            )
                        );
                    }

                    loading.remove();

                    currentConversationId =
                        data.conversation_id;

                    appendMessage(
                        "assistant",
                        data.response
                    );

                    await loadConversations();

                    return;
                }

                /*
                 * ====================================================
                 * NORMAL CHAT - STREAMING
                 * ====================================================
                 */

                const response =
                    await fetch(
                        `${API_BASE}/api/chat/stream`,
                        {
                            method: "POST",
                            headers: {
                                "Content-Type":
                                    "application/json"
                            },
                            body:
                                JSON.stringify(
                                    requestBody
                                )
                        }
                    );

                if (!response.ok) {
                    let data = null;

                    try {
                        data =
                            await response.json();
                    } catch {
                        // Response was not JSON.
                    }

                    throw new Error(
                        getErrorMessage(
                            data,
                            `Server returned HTTP ${response.status}`
                        )
                    );
                }

                if (!response.body) {
                    throw new Error(
                        "Streaming response body is unavailable."
                    );
                }

                loading.remove();

                const assistantMessage =
                    appendMessage(
                        "assistant",
                        ""
                    );

                const assistantContent =
                    assistantMessage.querySelector(
                        ".message-content"
                    );

                const reader =
                    response.body.getReader();

                const decoder =
                    new TextDecoder();

                let fullResponse = "";

                while (true) {
                    const {
                        value,
                        done
                    } =
                        await reader.read();

                    if (done) {
                        break;
                    }

                    const chunk =
                        decoder.decode(
                            value,
                            {
                                stream: true
                            }
                        );

                    if (!chunk) {
                        continue;
                    }

                    fullResponse += chunk;

                    assistantContent.innerHTML =
                        renderMarkdown(
                            fullResponse
                        );

                    messagesEl.scrollTop =
                        messagesEl.scrollHeight;
                }

                const remaining =
                    decoder.decode();

                if (remaining) {
                    fullResponse +=
                        remaining;

                    assistantContent.innerHTML =
                        renderMarkdown(
                            fullResponse
                        );

                    messagesEl.scrollTop =
                        messagesEl.scrollHeight;
                }

                await loadConversations();

            } catch (error) {
                loading.remove();

                appendMessage(
                    "assistant",
                    `Error: ${
                        error.message ||
                        "Something went wrong."
                    }`
                );
            } finally {
                sendButton.disabled = false;
                messageInput.disabled = false;
                messageInput.focus();
            }
        }
    );
}

/* ============================================================
   LOAD CONVERSATIONS
============================================================ */

async function loadConversations() {
    if (!conversationListEl) {
        return;
    }

    try {
        const response =
            await fetch(
                `${API_BASE}/api/conversations/${currentUserId}`
            );

        let data;

        try {
            data =
                await response.json();
        } catch {
            throw new Error(
                `Server returned HTTP ${response.status}`
            );
        }

        if (!response.ok) {
            throw new Error(
                getErrorMessage(
                    data,
                    "Unable to load conversations."
                )
            );
        }

        conversationListEl.innerHTML = "";

        if (data.length === 0) {
            conversationListEl.innerHTML = `
                <div class="empty-conversations">
                    No conversations yet.
                </div>
            `;

            return;
        }

        data.forEach(
            conversation => {
                const item =
                    document.createElement(
                        "div"
                    );

                item.className =
                    "conversation-item";

                if (
                    currentConversationId ===
                    conversation.id
                ) {
                    item.classList.add(
                        "active"
                    );
                }

                item.innerHTML = `
                    <button
                        class="conversation-open"
                        type="button"
                    >
                        <span
                            class="conversation-title"
                        >
                            ${escapeHtml(
                                conversation.title ||
                                "New Conversation"
                            )}
                        </span>
                    </button>

                    <button
                        class="conversation-delete"
                        type="button"
                        title="Delete conversation"
                    >
                        DELETE
                    </button>
                `;

                const openButton =
                    item.querySelector(
                        ".conversation-open"
                    );

                const deleteButton =
                    item.querySelector(
                        ".conversation-delete"
                    );

                openButton.addEventListener(
                    "click",
                    () =>
                        loadConversation(
                            conversation.id
                        )
                );

                deleteButton.addEventListener(
                    "click",
                    event => {
                        event.stopPropagation();

                        deleteConversation(
                            conversation.id
                        );
                    }
                );

                conversationListEl.appendChild(
                    item
                );
            }
        );

    } catch (error) {
        conversationListEl.innerHTML = `
            <div class="empty-conversations">
                Unable to load conversations.
            </div>
        `;
    }
}

/* ============================================================
   LOAD CONVERSATION
============================================================ */

async function loadConversation(
    conversationId
) {
    try {
        const response =
            await fetch(
                `${API_BASE}/api/conversations/${currentUserId}/${conversationId}`
            );

        let data;

        try {
            data =
                await response.json();
        } catch {
            throw new Error(
                `Server returned HTTP ${response.status}`
            );
        }

        if (!response.ok) {
            throw new Error(
                getErrorMessage(
                    data,
                    "Conversation not found."
                )
            );
        }

        currentConversationId =
            data.id;

        messagesEl.innerHTML = "";

        data.messages.forEach(
            message => {
                appendMessage(
                    message.role,
                    message.content
                );
            }
        );

        await loadConversations();

        messageInput.focus();

    } catch (error) {
        alert(
            error.message ||
            "Unable to load conversation."
        );
    }
}

/* ============================================================
   DELETE CONVERSATION
============================================================ */

async function deleteConversation(
    conversationId
) {
    const confirmed =
        confirm(
            "Delete this conversation?"
        );

    if (!confirmed) {
        return;
    }

    try {
        const response =
            await fetch(
                `${API_BASE}/api/conversations/${currentUserId}/${conversationId}`,
                {
                    method: "DELETE"
                }
            );

        let data;

        try {
            data =
                await response.json();
        } catch {
            throw new Error(
                `Server returned HTTP ${response.status}`
            );
        }

        if (!response.ok) {
            throw new Error(
                getErrorMessage(
                    data,
                    "Unable to delete conversation."
                )
            );
        }

        if (
            currentConversationId ===
            conversationId
        ) {
            currentConversationId = null;

            messagesEl.innerHTML = `
                <div class="welcome">
                    <h2>How can I help?</h2>
                    <p>
                        Start a new conversation.
                    </p>
                </div>
            `;
        }

        await loadConversations();

    } catch (error) {
        alert(
            error.message ||
            "Unable to delete conversation."
        );
    }
}

/* ============================================================
   DISPLAY MESSAGE
============================================================ */

function appendMessage(
    role,
    content
) {
    const message =
        document.createElement(
            "div"
        );

    message.className =
        `message ${role}`;

    const messageContent =
        document.createElement(
            "div"
        );

    messageContent.className =
        "message-content";

    if (role === "user") {
        messageContent.textContent =
            String(content);
    } else {
        messageContent.innerHTML =
            renderMarkdown(content);
    }

    message.appendChild(
        messageContent
    );

    messagesEl.appendChild(
        message
    );

    messagesEl.scrollTop =
        messagesEl.scrollHeight;

    return message;
}

/* ============================================================
   MARKDOWN RENDERER
============================================================ */

function renderMarkdown(value) {
    let text =
        String(value ?? "");

    text =
        text.replaceAll(
            "\r\n",
            "\n"
        );

    text =
        text.replaceAll(
            "\r",
            "\n"
        );

    /*
     * Protect fenced code blocks.
     */

    const codeBlocks = [];

    text =
        text.replace(
            /```([\s\S]*?)```/g,
            (match, code) => {
                const index =
                    codeBlocks.length;

                codeBlocks.push(
                    code
                        .replace(
                            /^\w+\n/,
                            ""
                        )
                        .trim()
                );

                return `@@CODEBLOCK_${index}@@`;
            }
        );

    /*
     * Escape HTML.
     */

    text =
        escapeHtml(text);

    /*
     * Headings.
     */

    text =
        text.replace(
            /^###### (.+)$/gm,
            "<h6>$1</h6>"
        );

    text =
        text.replace(
            /^##### (.+)$/gm,
            "<h5>$1</h5>"
        );

    text =
        text.replace(
            /^#### (.+)$/gm,
            "<h4>$1</h4>"
        );

    text =
        text.replace(
            /^### (.+)$/gm,
            "<h3>$1</h3>"
        );

    text =
        text.replace(
            /^## (.+)$/gm,
            "<h2>$1</h2>"
        );

    text =
        text.replace(
            /^# (.+)$/gm,
            "<h1>$1</h1>"
        );

    /*
     * Bold.
     */

    text =
        text.replace(
            /\*\*(.+?)\*\*/g,
            "<strong>$1</strong>"
        );

    text =
        text.replace(
            /__(.+?)__/g,
            "<strong>$1</strong>"
        );

    /*
     * Italic.
     */

    text =
        text.replace(
            /(?<!\*)\*([^\*\n]+)\*(?!\*)/g,
            "<em>$1</em>"
        );

    text =
        text.replace(
            /(?<!_)_([^_\n]+)_(?!_)/g,
            "<em>$1</em>"
        );

    /*
     * Inline code.
     */

    text =
        text.replace(
            /`([^`\n]+)`/g,
            "<code>$1</code>"
        );

    /*
     * Markdown links.
     */

    text =
        text.replace(
            /\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)/g,
            '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>'
        );

    /*
     * Horizontal rule.
     */

    text =
        text.replace(
            /^(---|\*\*\*|___)$/gm,
            "<hr>"
        );

    /*
     * Blockquotes.
     */

    text =
        text.replace(
            /^&gt;\s?(.+)$/gm,
            "<blockquote>$1</blockquote>"
        );

    /*
     * Unordered lists.
     */

    text =
        text.replace(
            /^\s*[-*+]\s+(.+)$/gm,
            "<li>$1</li>"
        );

    /*
     * Ordered lists.
     */

    text =
        text.replace(
            /^\s*\d+\.\s+(.+)$/gm,
            "<li>$1</li>"
        );

    /*
     * Wrap consecutive list items.
     */

    text =
        text.replace(
            /((?:<li>[\s\S]*?<\/li>\s*)+)/g,
            "<ul>$1</ul>"
        );

    /*
     * Tables.
     */

    text =
        renderMarkdownTables(text);

    /*
     * Paragraphs and line breaks.
     */

    const blocks =
        text.split(/\n{2,}/);

    const formattedBlocks = [];

    blocks.forEach(
        block => {
            const trimmed =
                block.trim();

            if (!trimmed) {
                return;
            }

            if (
                trimmed.startsWith("<h1>") ||
                trimmed.startsWith("<h2>") ||
                trimmed.startsWith("<h3>") ||
                trimmed.startsWith("<h4>") ||
                trimmed.startsWith("<h5>") ||
                trimmed.startsWith("<h6>") ||
                trimmed.startsWith("<ul>") ||
                trimmed.startsWith("<blockquote>") ||
                trimmed.startsWith("<hr>") ||
                trimmed.startsWith(
                    '<div class="markdown-table-wrapper">'
                )
            ) {
                formattedBlocks.push(
                    trimmed
                );
            } else {
                formattedBlocks.push(
                    `<p>${trimmed.replace(
                        /\n/g,
                        "<br>"
                    )}</p>`
                );
            }
        }
    );

    text =
        formattedBlocks.join("");

    /*
     * Restore code blocks.
     */

    text =
        text.replace(
            /@@CODEBLOCK_(\d+)@@/g,
            (match, index) => {
                const code =
                    escapeHtml(
                        codeBlocks[
                            Number(index)
                        ]
                    );

                return `
                    <pre>
                        <code>${code}</code>
                    </pre>
                `;
            }
        );

    return `
        <div class="markdown-body">
            ${text}
        </div>
    `;
}

/* ============================================================
   MARKDOWN TABLE RENDERER
============================================================ */

function renderMarkdownTables(text) {
    const lines =
        text.split("\n");

    const output = [];

    let index = 0;

    while (
        index < lines.length
    ) {
        const current =
            lines[index];

        const next =
            lines[index + 1];

        const isTable =
            current &&
            next &&
            current.includes("|") &&
            /^\s*\|?\s*:?-+:?\s*(\|\s*:?-+:?\s*)+\|?\s*$/
                .test(next);

        if (isTable) {
            const headers =
                parseTableRow(
                    current
                );

            const rows = [];

            index += 2;

            while (
                index < lines.length &&
                lines[index].includes("|") &&
                lines[index].trim() !== ""
            ) {
                rows.push(
                    parseTableRow(
                        lines[index]
                    )
                );

                index++;
            }

            let html = `
                <div class="markdown-table-wrapper">
                    <table class="markdown-table">
                        <thead>
                            <tr>
            `;

            headers.forEach(
                header => {
                    html += `
                        <th>
                            ${header}
                        </th>
                    `;
                }
            );

            html += `
                            </tr>
                        </thead>
                        <tbody>
            `;

            rows.forEach(
                row => {
                    html += `
                        <tr>
                    `;

                    row.forEach(
                        cell => {
                            html += `
                                <td>
                                    ${cell}
                                </td>
                            `;
                        }
                    );

                    html += `
                        </tr>
                    `;
                }
            );

            html += `
                        </tbody>
                    </table>
                </div>
            `;

            output.push(
                html
            );

            continue;
        }

        output.push(
            current
        );

        index++;
    }

    return output.join("\n");
}

/* ============================================================
   PARSE TABLE ROW
============================================================ */

function parseTableRow(row) {
    return row
        .trim()
        .replace(/^\|/, "")
        .replace(/\|$/, "")
        .split("|")
        .map(
            cell =>
                cell.trim()
        );
}

/* ============================================================
   HTML ESCAPING
============================================================ */

function escapeHtml(value) {
    return String(value)
        .replaceAll(
            "&",
            "&amp;"
        )
        .replaceAll(
            "<",
            "&lt;"
        )
        .replaceAll(
            ">",
            "&gt;"
        )
        .replaceAll(
            '"',
            "&quot;"
        )
        .replaceAll(
            "'",
            "&#039;"
        );
}

/* ============================================================
   DATABASE BUTTON
============================================================ */

if (databaseButton) {
    databaseButton.addEventListener(
        "click",
        async () => {
            chatView.classList.add(
                "hidden"
            );

            comparisonView.classList.add(
                "hidden"
            );

            databaseView.classList.remove(
                "hidden"
            );

            pageTitle.textContent =
                "Database Viewer";

            await loadDatabaseTable(
                currentDatabaseTable
            );
        }
    );
}

/* ============================================================
   DATABASE TABS
============================================================ */

if (databaseTabs) {
    databaseTabs.forEach(
        tab => {
            tab.addEventListener(
                "click",
                async () => {
                    databaseTabs.forEach(
                        item => {
                            item.classList.remove(
                                "active"
                            );
                        }
                    );

                    tab.classList.add(
                        "active"
                    );

                    currentDatabaseTable =
                        tab.dataset.table;

                    await loadDatabaseTable(
                        currentDatabaseTable
                    );
                }
            );
        }
    );
}

/* ============================================================
   REFRESH DATABASE
============================================================ */

if (refreshDatabase) {
    refreshDatabase.addEventListener(
        "click",
        async () => {
            await loadDatabaseTable(
                currentDatabaseTable
            );
        }
    );
}

/* ============================================================
   LOAD DATABASE TABLE
============================================================ */

async function loadDatabaseTable(
    table
) {
    databaseContent.innerHTML = `
        <div class="database-loading">
            Loading...
        </div>
    `;

    try {
        const response =
            await fetch(
                `${API_BASE}/api/database/${table}`
            );

        let data;

        try {
            data =
                await response.json();
        } catch {
            throw new Error(
                `Server returned HTTP ${response.status}`
            );
        }

        if (!response.ok) {
            throw new Error(
                getErrorMessage(
                    data,
                    "Unable to load database data."
                )
            );
        }

        renderDatabaseTable(
            table,
            data
        );

    } catch (error) {
        databaseContent.innerHTML = `
            <div class="database-error">
                ${escapeHtml(
                    error.message ||
                    "Unable to load database data."
                )}
            </div>
        `;
    }
}

/* ============================================================
   RENDER DATABASE TABLE
============================================================ */

function renderDatabaseTable(
    table,
    rows
) {
    if (!rows.length) {
        databaseContent.innerHTML = `
            <div class="database-empty">
                No records found.
            </div>
        `;

        return;
    }

    const columns =
        Object.keys(
            rows[0]
        );

    const tableElement =
        document.createElement(
            "table"
        );

    tableElement.className =
        "data-table";

    const thead =
        document.createElement(
            "thead"
        );

    const headerRow =
        document.createElement(
            "tr"
        );

    columns.forEach(
        column => {
            const th =
                document.createElement(
                    "th"
                );

            th.textContent =
                formatColumnName(
                    column
                );

            headerRow.appendChild(
                th
            );
        }
    );

    thead.appendChild(
        headerRow
    );

    const tbody =
        document.createElement(
            "tbody"
        );

    rows.forEach(
        row => {
            const tr =
                document.createElement(
                    "tr"
                );

            columns.forEach(
                column => {
                    const td =
                        document.createElement(
                            "td"
                        );

                    const value =
                        row[column];

                    td.textContent =
                        value === null ||
                        value === undefined
                            ? "-"
                            : String(value);

                    tr.appendChild(
                        td
                    );
                }
            );

            tbody.appendChild(
                tr
            );
        }
    );

    tableElement.appendChild(
        thead
    );

    tableElement.appendChild(
        tbody
    );

    databaseContent.innerHTML =
        "";

    databaseContent.appendChild(
        tableElement
    );
}

/* ============================================================
   FORMAT COLUMN NAME
============================================================ */

function formatColumnName(
    value
) {
    return value
        .replaceAll(
            "_",
            " "
        )
        .replace(
            /\b\w/g,
            char =>
                char.toUpperCase()
        );
}

/* ============================================================
   OPEN COMPARISON
============================================================ */

function openComparison() {
    chatView.classList.add(
        "hidden"
    );

    databaseView.classList.add(
        "hidden"
    );

    comparisonView.classList.remove(
        "hidden"
    );

    pageTitle.textContent =
        "Prompt Comparison";

    comparisonTask.focus();
}

/* ============================================================
   CLOSE COMPARISON
============================================================ */

function closeComparison() {
    comparisonView.classList.add(
        "hidden"
    );

    chatView.classList.remove(
        "hidden"
    );

    pageTitle.textContent =
        "AI Assistant";
}

if (backToChat) {
    backToChat.addEventListener(
        "click",
        closeComparison
    );
}

/* ============================================================
   COMPARE BUTTON
============================================================ */

if (compareButton) {
    compareButton.addEventListener(
        "click",
        comparePrompts
    );
}

/* ============================================================
   COMPARE PROMPTS
============================================================ */

async function comparePrompts() {
    const task =
        comparisonTask.value.trim();

    if (!task) {
        alert(
            "Please enter a task to compare."
        );

        return;
    }

    const techniques = [
        comparisonTechnique1.value,
        comparisonTechnique2.value
    ];

    if (
        techniques[0] ===
        techniques[1]
    ) {
        alert(
            "Please select two different prompting techniques."
        );

        return;
    }

    compareButton.disabled =
        true;

    comparisonLoading.classList.remove(
        "hidden"
    );

    comparisonResults.innerHTML =
        "";

    /*
     * Comparison endpoint expects examples
     * as a list of objects.
     *
     * We therefore parse the same UI text
     * separately for comparison.
     */

    const rawExamples =
        examplesInput
            ? examplesInput.value.trim()
            : "";

    const comparisonExamples =
        parseExamplesForComparison(
            rawExamples
        );

    const requestBody = {
        task: task,

        techniques: techniques,

        role:
            comparisonRole.value.trim() ||
            null,

        examples:
            comparisonExamples,

        context:
            comparisonContext.value.trim() ||
            null,

        constraints:
            comparisonConstraints.value.trim() ||
            null,

        expected_output:
            comparisonExpected.value.trim() ||
            null,

        model:
            modelSelect.value,

        temperature:
            Number(
                temperatureInput.value
            ),

        top_p:
            Number(
                topPInput.value
            ),

        max_tokens:
            Number(
                maxTokensInput.value
            )
    };

    try {
        const response =
            await fetch(
                `${API_BASE}/api/v1/comparison/`,
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body:
                        JSON.stringify(
                            requestBody
                        )
                }
            );

        let data;

        try {
            data =
                await response.json();
        } catch {
            throw new Error(
                `Server returned HTTP ${response.status}`
            );
        }

        if (!response.ok) {
            throw new Error(
                getErrorMessage(
                    data,
                    "Prompt comparison failed."
                )
            );
        }

        renderComparisonResults(
            data
        );

    } catch (error) {
        comparisonResults.innerHTML = `
            <div class="database-error">
                ${escapeHtml(
                    error.message ||
                    "Prompt comparison failed."
                )}
            </div>
        `;

    } finally {
        comparisonLoading.classList.add(
            "hidden"
        );

        compareButton.disabled =
            false;
    }
}

/* ============================================================
   PARSE EXAMPLES FOR COMPARISON
============================================================ */

function parseExamplesForComparison(
    rawExamples
) {
    if (!rawExamples) {
        return [];
    }

    const blocks =
        rawExamples
            .replace(/\r\n/g, "\n")
            .split(/\n\s*\n+/)
            .map(
                block =>
                    block.trim()
            )
            .filter(Boolean);

    return blocks
        .map(block => {
            const inputMatch =
                block.match(
                    /Input\s*:\s*([\s\S]*?)(?=\n\s*(?:Output|Expected Output)\s*:|$)/i
                );

            const outputMatch =
                block.match(
                    /(?:Output|Expected Output)\s*:\s*([\s\S]*)/i
                );

            if (
                !inputMatch ||
                !outputMatch
            ) {
                return null;
            }

            return {
                input:
                    inputMatch[1].trim(),

                output:
                    outputMatch[1].trim()
            };
        })
        .filter(Boolean);
}

/* ============================================================
   RENDER COMPARISON RESULTS
============================================================ */

function renderComparisonResults(
    data
) {
    if (
        !data.results ||
        data.results.length === 0
    ) {
        comparisonResults.innerHTML = `
            <div class="database-empty">
                No comparison results returned.
            </div>
        `;

        return;
    }

    comparisonResults.innerHTML =
        data.results
            .map(
                result => `
                    <article
                        class="comparison-card"
                    >
                        <div
                            class="comparison-card-header"
                        >
                            <h3>
                                ${escapeHtml(
                                    formatTechnique(
                                        result.technique
                                    )
                                )}
                            </h3>

                            <div
                                class="comparison-meta"
                            >
                                Model:
                                ${escapeHtml(
                                    result.model
                                )}
                                |
                                Temperature:
                                ${result.temperature}
                                |
                                Top-P:
                                ${result.top_p}
                                |
                                Max Tokens:
                                ${result.max_tokens}
                                |
                                ${result.execution_time_ms}
                                ms
                            </div>
                        </div>

                        <div
                            class="comparison-card-body"
                        >
                            <h4>
                                Generated Prompt
                            </h4>

                            <div
                                class="comparison-prompt"
                            >
                                ${escapeHtml(
                                    result.prompt
                                )}
                            </div>

                            <h4>
                                Model Response
                            </h4>

                            <div
                                class="comparison-response"
                            >
                                ${renderMarkdown(
                                    result.response
                                )}
                            </div>
                        </div>
                    </article>
                `
            )
            .join("");
}

/* ============================================================
   FORMAT TECHNIQUE NAME
============================================================ */

function formatTechnique(
    technique
) {
    return String(technique)
        .replaceAll(
            "-",
            " "
        )
        .replace(
            /\b\w/g,
            char =>
                char.toUpperCase()
        );
}

/* ============================================================
   COMPARISON BUTTON
============================================================ */

if (comparisonButton) {
    comparisonButton.addEventListener(
        "click",
        openComparison
    );
}

