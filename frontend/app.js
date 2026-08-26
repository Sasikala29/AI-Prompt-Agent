const API_BASE = "";

let currentConversationId = null;
const currentUserId = 1;

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


document.addEventListener("DOMContentLoaded", async () => {

    updateTechniqueFields();

    if (temperatureInput) {
        temperatureInput.addEventListener("input", () => {
            temperatureValue.textContent = temperatureInput.value;
        });
    }

    if (topPInput) {
        topPInput.addEventListener("input", () => {
            topPValue.textContent = topPInput.value;
        });
    }

    await loadConversations();
});


/* ------------------------------------------------------------
   NEW CHAT
------------------------------------------------------------ */

newChatButton.addEventListener("click", () => {
    currentConversationId = null;

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


/* ------------------------------------------------------------
   PROMPT TECHNIQUE DROPDOWN
------------------------------------------------------------ */

techniqueSelect.addEventListener(
    "change",
    updateTechniqueFields
);


function updateTechniqueFields() {

    const technique = techniqueSelect.value;

    hideAllTechniqueFields();

    if (technique === "one-shot") {
        examplesField.classList.remove("hidden");
    }

    if (technique === "few-shot") {
        examplesField.classList.remove("hidden");
    }

    if (technique === "role-based") {
        roleField.classList.remove("hidden");
    }

    if (technique === "structured") {
        roleField.classList.remove("hidden");
        contextField.classList.remove("hidden");
        constraintsField.classList.remove("hidden");
        expectedOutputField.classList.remove("hidden");
        examplesField.classList.remove("hidden");
    }
}


function hideAllTechniqueFields() {

    roleField.classList.add("hidden");
    contextField.classList.add("hidden");
    constraintsField.classList.add("hidden");
    expectedOutputField.classList.add("hidden");
    examplesField.classList.add("hidden");
}


/* ------------------------------------------------------------
   CHAT SUBMIT
------------------------------------------------------------ */

chatForm.addEventListener("submit", async (event) => {

    event.preventDefault();

    const message = messageInput.value.trim();

    if (!message) {
        return;
    }

    appendMessage("user", message);

    messageInput.value = "";

    sendButton.disabled = true;
    messageInput.disabled = true;

    const loading = appendMessage(
        "assistant",
        "Thinking..."
    );

    try {

        const requestBody = {
            message: message,
            conversation_id: currentConversationId,
            user_id: currentUserId,
            model: modelSelect.value,
            temperature: Number(temperatureInput.value),
            top_p: Number(topPInput.value),
            max_tokens: Number(maxTokensInput.value),
            response_format: responseFormatSelect.value,
            technique: techniqueSelect.value,
            role: roleInput.value.trim() || null,
            context: contextInput.value.trim() || null,
            constraints: constraintsInput.value.trim() || null,
            expected_output: expectedOutputInput.value.trim() || null,
            examples: examplesInput.value.trim() || null
        };

        const endpoint =
            modeSelect.value === "agent"
                ? `${API_BASE}/api/agent/chat`
                : `${API_BASE}/api/chat`;


        const response = await fetch(
            endpoint,
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify(requestBody)
            }
        );


        const data = await response.json();


        if (!response.ok) {
            throw new Error(
                data.detail ||
                "Unable to get a response."
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

    } catch (error) {

        loading.remove();

        appendMessage(
            "assistant",
            `Error: ${error.message}`
        );

    } finally {

        sendButton.disabled = false;
        messageInput.disabled = false;
        messageInput.focus();
    }
});


/* ------------------------------------------------------------
   LOAD CONVERSATIONS
------------------------------------------------------------ */

async function loadConversations() {

    try {

        const response = await fetch(
            `${API_BASE}/api/conversations/${currentUserId}`
        );


        if (!response.ok) {
            throw new Error(
                "Unable to load conversations."
            );
        }


        const conversations =
            await response.json();


        conversationListEl.innerHTML = "";


        if (conversations.length === 0) {

            conversationListEl.innerHTML = `
                <div class="empty-conversations">
                    No conversations yet.
                </div>
            `;

            return;
        }


        conversations.forEach(
            (conversation) => {

                const item =
                    document.createElement("div");

                item.className =
                    "conversation-item";


                if (
                    currentConversationId ===
                    conversation.id
                ) {
                    item.classList.add("active");
                }


                item.innerHTML = `
                    <button
                        class="conversation-open"
                        type="button">

                        <span
                            class="conversation-title">

                            ${escapeHtml(
                                conversation.title ||
                                "New Conversation"
                            )}

                        </span>

                    </button>


                    <button
                        class="conversation-delete"
                        type="button"
                        title="Delete conversation">

                        DELETE

                    </button>
                `;


                item
                    .querySelector(
                        ".conversation-open"
                    )
                    .addEventListener(
                        "click",
                        () =>
                            loadConversation(
                                conversation.id
                            )
                    );


                item
                    .querySelector(
                        ".conversation-delete"
                    )
                    .addEventListener(
                        "click",
                        (event) => {

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


/* ------------------------------------------------------------
   LOAD CONVERSATION
------------------------------------------------------------ */

async function loadConversation(
    conversationId
) {

    try {

        const response = await fetch(
            `${API_BASE}/api/conversations/${currentUserId}/${conversationId}`
        );


        const data =
            await response.json();


        if (!response.ok) {

            throw new Error(
                data.detail ||
                "Conversation not found."
            );
        }


        currentConversationId =
            data.id;


        messagesEl.innerHTML = "";


        data.messages.forEach(
            (message) => {

                appendMessage(
                    message.role,
                    message.content
                );
            }
        );


        await loadConversations();

        messageInput.focus();

    } catch (error) {

        alert(error.message);
    }
}


/* ------------------------------------------------------------
   DELETE CONVERSATION
------------------------------------------------------------ */

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

        const response = await fetch(
            `${API_BASE}/api/conversations/${currentUserId}/${conversationId}`,
            {
                method: "DELETE"
            }
        );


        const data =
            await response.json();


        if (!response.ok) {

            throw new Error(
                data.detail ||
                "Unable to delete conversation."
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

        alert(error.message);
    }
}


/* ------------------------------------------------------------
   DISPLAY MESSAGE
------------------------------------------------------------ */

function appendMessage(
    role,
    content
) {

    const message =
        document.createElement("div");


    message.className =
        `message ${role}`;


    message.innerHTML = `
        <div class="message-content">
            ${escapeHtml(content)}
        </div>
    `;


    messagesEl.appendChild(message);

    messagesEl.scrollTop =
        messagesEl.scrollHeight;


    return message;
}


/* ------------------------------------------------------------
   HTML ESCAPING
------------------------------------------------------------ */

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


databaseButton.addEventListener("click", async () => {

    chatView.classList.add("hidden");
    databaseView.classList.remove("hidden");

    pageTitle.textContent = "Database Viewer";

    await loadDatabaseTable(currentDatabaseTable);
});


newChatButton.addEventListener("click", () => {

    databaseView.classList.add("hidden");
    chatView.classList.remove("hidden");

    pageTitle.textContent = "AI Assistant";
});


databaseTabs.forEach((tab) => {

    tab.addEventListener("click", async () => {

        databaseTabs.forEach((item) => {
            item.classList.remove("active");
        });

        tab.classList.add("active");

        currentDatabaseTable =
            tab.dataset.table;

        await loadDatabaseTable(
            currentDatabaseTable
        );
    });
});


refreshDatabase.addEventListener(
    "click",
    async () => {
        await loadDatabaseTable(
            currentDatabaseTable
        );
    }
);


async function loadDatabaseTable(table) {

    databaseContent.innerHTML =
        `<div class="database-loading">Loading...</div>`;

    try {

        const response = await fetch(
            `${API_BASE}/api/database/${table}`
        );

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                data.detail ||
                "Unable to load database data."
            );
        }

        renderDatabaseTable(
            table,
            data
        );

    } catch (error) {

        databaseContent.innerHTML = `
            <div class="database-error">
                ${escapeHtml(error.message)}
            </div>
        `;
    }
}


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
        Object.keys(rows[0]);

    const tableElement =
        document.createElement("table");

    tableElement.className =
        "data-table";

    const thead =
        document.createElement("thead");

    const headerRow =
        document.createElement("tr");

    columns.forEach((column) => {

        const th =
            document.createElement("th");

        th.textContent =
            formatColumnName(column);

        headerRow.appendChild(th);
    });

    thead.appendChild(headerRow);

    const tbody =
        document.createElement("tbody");

    rows.forEach((row) => {

        const tr =
            document.createElement("tr");

        columns.forEach((column) => {

            const td =
                document.createElement("td");

            const value =
                row[column];

            td.textContent =
                value === null ||
                value === undefined
                    ? "-"
                    : String(value);

            tr.appendChild(td);
        });

        tbody.appendChild(tr);
    });

    tableElement.appendChild(thead);
    tableElement.appendChild(tbody);

    databaseContent.innerHTML = "";

    databaseContent.appendChild(
        tableElement
    );
}


function formatColumnName(value) {

    return value
        .replaceAll("_", " ")
        .replace(/\b\w/g, char =>
            char.toUpperCase()
        );
}


/* ============================================================
   PROMPT COMPARISON
============================================================ */

const comparisonView =
    document.getElementById("comparisonView");

const comparisonTask =
    document.getElementById("comparisonTask");

const comparisonTechnique1 =
    document.getElementById("comparisonTechnique1");

const comparisonTechnique2 =
    document.getElementById("comparisonTechnique2");

const comparisonRole =
    document.getElementById("comparisonRole");

const comparisonExpected =
    document.getElementById("comparisonExpected");

const comparisonContext =
    document.getElementById("comparisonContext");

const comparisonConstraints =
    document.getElementById("comparisonConstraints");

const compareButton =
    document.getElementById("compareButton");

const comparisonResults =
    document.getElementById("comparisonResults");

const comparisonLoading =
    document.getElementById("comparisonLoading");

const backToChat =
    document.getElementById("backToChat");


function openComparison() {

    chatView.classList.add("hidden");
    databaseView.classList.add("hidden");

    comparisonView.classList.remove("hidden");

    pageTitle.textContent =
        "Prompt Comparison";

    comparisonTask.focus();
}


function closeComparison() {

    comparisonView.classList.add("hidden");

    chatView.classList.remove("hidden");

    pageTitle.textContent =
        "AI Assistant";
}


if (backToChat) {

    backToChat.addEventListener(
        "click",
        closeComparison
    );
}


if (compareButton) {

    compareButton.addEventListener(
        "click",
        comparePrompts
    );
}


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
        comparisonTechnique2.value,
    ];


    if (techniques[0] === techniques[1]) {

        alert(
            "Please select two different prompting techniques."
        );

        return;
    }


    compareButton.disabled = true;

    comparisonLoading.classList.remove(
        "hidden"
    );

    comparisonResults.innerHTML = "";


    const requestBody = {

        task: task,

        techniques: techniques,

        role:
            comparisonRole.value.trim() ||
            null,

        examples: [],

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
            Number(temperatureInput.value),

        top_p:
            Number(topPInput.value),

        max_tokens:
            Number(maxTokensInput.value),
    };


    try {

        const response =
            await fetch(
                `${API_BASE}/api/v1/comparison/`,
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json",
                    },

                    body:
                        JSON.stringify(
                            requestBody
                        ),
                }
            );


        const data =
            await response.json();


        if (!response.ok) {

            throw new Error(
                data.detail ||
                "Prompt comparison failed."
            );
        }


        renderComparisonResults(
            data
        );


    } catch (error) {

        comparisonResults.innerHTML = `
            <div class="database-error">
                ${escapeHtml(error.message)}
            </div>
        `;

    } finally {

        comparisonLoading.classList.add(
            "hidden"
        );

        compareButton.disabled = false;
    }
}


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
                (result) => `
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
                                ââ ¢â¬â¢¢â¬ ¢¢âš¬¢âž¢â¢¢âš¬ ¢¢¢â¬¡¬¢¢â¬¾¢ââ ¢â¬â¢¢â¬¡âš¢ââš¢¢¢¢â¬¡¬â¦¡¢â¬¡âš¬â¢¢âš¬¦¢â¬¡âš¡ââ ¢â¬â¢¢â¬ ¢¢âš¬¢âž¢ââš¢¢¢¢âš¬¡âš¬¢â¬¦âš¡ââ ¢â¬â¢¢¢¢â¬¡¬â¦¡â¢¢âš¬¡¢â¬¡âš·
                                Temperature:
                                ${result.temperature}
                                ââ ¢â¬â¢¢â¬ ¢¢âš¬¢âž¢â¢¢âš¬ ¢¢¢â¬¡¬¢¢â¬¾¢ââ ¢â¬â¢¢â¬¡âš¢ââš¢¢¢¢â¬¡¬â¦¡¢â¬¡âš¬â¢¢âš¬¦¢â¬¡âš¡ââ ¢â¬â¢¢â¬ ¢¢âš¬¢âž¢ââš¢¢¢¢âš¬¡âš¬¢â¬¦âš¡ââ ¢â¬â¢¢¢¢â¬¡¬â¦¡â¢¢âš¬¡¢â¬¡âš·
                                Top-P:
                                ${result.top_p}
                                ââ ¢â¬â¢¢â¬ ¢¢âš¬¢âž¢â¢¢âš¬ ¢¢¢â¬¡¬¢¢â¬¾¢ââ ¢â¬â¢¢â¬¡âš¢ââš¢¢¢¢â¬¡¬â¦¡¢â¬¡âš¬â¢¢âš¬¦¢â¬¡âš¡ââ ¢â¬â¢¢â¬ ¢¢âš¬¢âž¢ââš¢¢¢¢âš¬¡âš¬¢â¬¦âš¡ââ ¢â¬â¢¢¢¢â¬¡¬â¦¡â¢¢âš¬¡¢â¬¡âš·
                                Max Tokens:
                                ${result.max_tokens}
                                ââ ¢â¬â¢¢â¬ ¢¢âš¬¢âž¢â¢¢âš¬ ¢¢¢â¬¡¬¢¢â¬¾¢ââ ¢â¬â¢¢â¬¡âš¢ââš¢¢¢¢â¬¡¬â¦¡¢â¬¡âš¬â¢¢âš¬¦¢â¬¡âš¡ââ ¢â¬â¢¢â¬ ¢¢âš¬¢âž¢ââš¢¢¢¢âš¬¡âš¬¢â¬¦âš¡ââ ¢â¬â¢¢¢¢â¬¡¬â¦¡â¢¢âš¬¡¢â¬¡âš·
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
                                ${escapeHtml(
                                    result.response
                                )}
                            </div>

                        </div>

                    </article>
                `
            )
            .join("");
}


function formatTechnique(
    technique
) {

    return technique
        .replaceAll("-", " ")
        .replace(
            /\b\w/g,
            char =>
                char.toUpperCase()
        );
}


const comparisonButton =
    document.getElementById("comparisonButton");

if (comparisonButton) {

    comparisonButton.addEventListener(
        "click",
        openComparison
    );
}

