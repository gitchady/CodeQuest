const state = {
  accessToken: localStorage.getItem("perminof.accessToken") || "",
  refreshToken: localStorage.getItem("perminof.refreshToken") || "",
  currentCourse: null,
};

const $ = (selector) => document.querySelector(selector);

function setStatus(message) {
  $("#apiStatus").textContent = message;
}

function setTokenStatus() {
  $("#tokenStatus").textContent = state.accessToken ? "Signed in" : "Guest";
  $("#logoutButton").classList.toggle("hidden", !state.accessToken);
}

async function request(path, options = {}) {
  const headers = new Headers(options.headers || {});
  headers.set("Content-Type", "application/json");
  if (state.accessToken) {
    headers.set("Authorization", `Bearer ${state.accessToken}`);
  }

  const response = await fetch(path, { ...options, headers });
  if (!response.ok) {
    const body = await response.json().catch(() => ({ message: response.statusText }));
    throw new Error(body.message || `HTTP ${response.status}`);
  }
  return response.status === 204 ? null : response.json();
}

function renderCourses(courses) {
  const list = $("#courseList");
  if (!courses.length) {
    list.innerHTML = '<p class="empty">No courses yet.</p>';
    return;
  }

  list.innerHTML = courses
    .map(
      (course) => `
        <button class="item-button" type="button" data-course-id="${course.id}">
          <strong>${escapeHtml(course.title)}</strong>
          <span>${escapeHtml(course.description)}</span>
        </button>
      `,
    )
    .join("");

  list.querySelectorAll("[data-course-id]").forEach((button) => {
    button.addEventListener("click", () => loadCourseStructure(button.dataset.courseId));
  });
}

async function loadCourses() {
  setStatus("Loading courses");
  try {
    const courses = await request("/api/courses");
    renderCourses(courses);
    setStatus("Courses loaded");
  } catch (error) {
    setStatus("API error");
    $("#courseList").innerHTML = `<p class="message">${escapeHtml(error.message)}</p>`;
  }
}

async function loadCourseStructure(courseId) {
  setStatus("Loading structure");
  const course = await request(`/api/courses/${courseId}/structure`);
  state.currentCourse = course;
  $("#courseTitle").textContent = course.title;
  renderStructure(course);
  setStatus("Structure loaded");
}

function renderStructure(course) {
  $("#structurePanel").innerHTML = course.modules
    .map(
      (module) => `
        <section class="module">
          <p class="module-title">${escapeHtml(module.title)}</p>
          ${module.sections.map(renderSection).join("")}
        </section>
      `,
    )
    .join("");

  document.querySelectorAll("[data-kind]").forEach((button) => {
    button.addEventListener("click", () => loadDetail(button.dataset.kind, button.dataset.id));
  });
}

function renderSection(section) {
  const lectures = section.lectures
    .map((lecture) => nodeButton("lecture", lecture.id, lecture.title, "Lecture"))
    .join("");
  const questions = section.question_ids
    .map((id, index) => nodeButton("question", id, `Question ${index + 1}`, "Interactive"))
    .join("");
  const tasks = section.tasks
    .map((task) => nodeButton("task", task.id, task.title, "Text task"))
    .join("");
  const codeTasks = section.code_tasks
    .map((task) => nodeButton("code-task", task.id, task.title, task.language))
    .join("");

  return `
    <div>
      <p class="section-title">${escapeHtml(section.title)}</p>
      <div class="list">${lectures}${questions}${tasks}${codeTasks}</div>
    </div>
  `;
}

function nodeButton(kind, id, title, label) {
  return `
    <button class="item-button" type="button" data-kind="${kind}" data-id="${id}">
      <strong>${escapeHtml(title)}</strong>
      <span>${escapeHtml(label)}</span>
    </button>
  `;
}

async function loadDetail(kind, id) {
  setStatus("Loading item");
  const paths = {
    lecture: `/api/lectures/${id}`,
    question: `/api/questions/${id}`,
    task: `/api/tasks/${id}`,
    "code-task": `/api/code-tasks/${id}`,
  };
  const detail = await request(paths[kind]);
  renderDetail(kind, detail);
  setStatus("Item loaded");
}

function renderDetail(kind, detail) {
  if (kind === "lecture") {
    $("#detailPanel").innerHTML = `
      <div>
        <h3>${escapeHtml(detail.title)}</h3>
        <div class="meta"><span>Lecture</span><span>Position ${detail.position}</span></div>
        <p>${escapeHtml(detail.content)}</p>
      </div>
    `;
    return;
  }

  if (kind === "question") {
    $("#detailPanel").innerHTML = `
      <div>
        <h3>${escapeHtml(detail.text)}</h3>
        <div class="meta"><span>Question</span><span>${detail.reward_points} points</span><span>${detail.max_attempts} attempts</span></div>
        <form id="questionForm" class="answer-list">
          ${detail.answer_options
            .map(
              (option) => `
                <label>
                  <input type="checkbox" name="answer" value="${option.id}">
                  <span>${escapeHtml(option.text)}</span>
                </label>
              `,
            )
            .join("")}
          <button type="submit">Submit answer</button>
          <p id="detailMessage" class="message"></p>
        </form>
      </div>
    `;
    $("#questionForm").addEventListener("submit", (event) => submitQuestion(event, detail.id));
    return;
  }

  if (kind === "task") {
    $("#detailPanel").innerHTML = `
      <div>
        <h3>${escapeHtml(detail.title)}</h3>
        <div class="meta"><span>Text task</span><span>${detail.reward_points} points</span><span>${detail.max_attempts} attempts</span></div>
        <p>${escapeHtml(detail.statement)}</p>
        <form id="taskForm" class="simple-form">
          <input id="taskAnswer" placeholder="Your answer" required>
          <button type="submit">Submit task</button>
          <p id="detailMessage" class="message"></p>
        </form>
      </div>
    `;
    $("#taskForm").addEventListener("submit", (event) => submitTask(event, detail.id));
    return;
  }

  $("#detailPanel").innerHTML = `
    <div>
      <h3>${escapeHtml(detail.title)}</h3>
      <div class="meta"><span>Code task</span><span>${escapeHtml(detail.language)}</span><span>${detail.time_limit_seconds}s</span><span>${detail.memory_limit_mb} MB</span></div>
      <p>${escapeHtml(detail.statement)}</p>
      <form id="codeForm" class="simple-form">
        <textarea id="sourceCode" spellcheck="false">${escapeHtml(detail.starter_code)}</textarea>
        <button type="submit">Submit code</button>
        <p id="detailMessage" class="message"></p>
      </form>
    </div>
  `;
  $("#codeForm").addEventListener("submit", (event) => submitCode(event, detail.id));
}

async function submitQuestion(event, questionId) {
  event.preventDefault();
  const selected = [...document.querySelectorAll('input[name="answer"]:checked')].map((input) => input.value);
  await submitLearning(`/api/learning/questions/${questionId}/attempts`, { selected_option_ids: selected });
}

async function submitTask(event, taskId) {
  event.preventDefault();
  await submitLearning(`/api/learning/tasks/${taskId}/attempts`, { submitted_answer: $("#taskAnswer").value });
}

async function submitCode(event, codeTaskId) {
  event.preventDefault();
  await submitLearning(`/api/learning/code-tasks/${codeTaskId}/submissions`, { source_code: $("#sourceCode").value });
}

async function submitLearning(path, body) {
  const message = $("#detailMessage");
  if (!state.accessToken) {
    message.textContent = "Sign in before submitting learning work.";
    return;
  }
  try {
    const result = await request(path, { method: "POST", body: JSON.stringify(body) });
    message.textContent = JSON.stringify(result, null, 2);
  } catch (error) {
    message.textContent = error.message;
  }
}

async function login(event) {
  event.preventDefault();
  try {
    const result = await request("/api/auth/login", {
      method: "POST",
      body: JSON.stringify({
        email: $("#emailInput").value,
        password: $("#passwordInput").value,
      }),
    });
    state.accessToken = result.access_token;
    state.refreshToken = result.refresh_token;
    localStorage.setItem("perminof.accessToken", state.accessToken);
    localStorage.setItem("perminof.refreshToken", state.refreshToken);
    setTokenStatus();
    setStatus("Signed in");
  } catch (error) {
    setStatus(error.message);
  }
}

function logout() {
  state.accessToken = "";
  state.refreshToken = "";
  localStorage.removeItem("perminof.accessToken");
  localStorage.removeItem("perminof.refreshToken");
  setTokenStatus();
  setStatus("Signed out");
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

$("#loginForm").addEventListener("submit", login);
$("#logoutButton").addEventListener("click", logout);
$("#refreshCourses").addEventListener("click", loadCourses);

setTokenStatus();
loadCourses();
