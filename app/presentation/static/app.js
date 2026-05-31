const state = {
  accessToken: localStorage.getItem("perminof.accessToken") || "",
  refreshToken: localStorage.getItem("perminof.refreshToken") || "",
  currentCourse: null,
  currentUser: null,
  courses: [],
};

const $ = (selector) => document.querySelector(selector);

function setStatus(message) {
  $("#apiStatus").textContent = message;
}

function setTokenStatus() {
  const role = state.currentUser?.role || "guest";
  $("#tokenStatus").textContent = state.accessToken ? `Signed in: ${role}` : "Guest";
  $("#logoutButton").classList.toggle("hidden", !state.accessToken);
  $("#studioUserRole").textContent = role;
  const canManage = role === "author" || role === "admin";
  $("#studioAccess").textContent = canManage
    ? "Create and extend learning content."
    : "Sign in as author or admin.";
  $("#studioView").classList.toggle("locked", !canManage);
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

function switchView(view) {
  const studio = view === "studio";
  $("#workspaceView").classList.toggle("hidden", studio);
  $("#studioView").classList.toggle("hidden", !studio);
  $("#workspaceTab").classList.toggle("active", !studio);
  $("#studioTab").classList.toggle("active", studio);
}

function renderCourses(courses) {
  state.courses = courses;
  $("#studioCourseCount").textContent = String(courses.length);
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
          <span>ID ${escapeHtml(course.id)}</span>
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

async function loadMe() {
  if (!state.accessToken) {
    state.currentUser = null;
    setTokenStatus();
    return;
  }
  try {
    state.currentUser = await request("/api/auth/me");
  } catch {
    state.accessToken = "";
    state.refreshToken = "";
    localStorage.removeItem("perminof.accessToken");
    localStorage.removeItem("perminof.refreshToken");
    state.currentUser = null;
  }
  setTokenStatus();
}

async function loadCourseStructure(courseId) {
  setStatus("Loading structure");
  const course = await request(`/api/courses/${courseId}/structure`);
  state.currentCourse = course;
  $("#courseTitle").textContent = course.title;
  $("#moduleCourseIdInput").value = course.id;
  renderStructure(course);
  setStatus("Structure loaded");
}

function renderStructure(course) {
  $("#structurePanel").innerHTML = course.modules
    .map(
      (module) => `
        <section class="module">
          <p class="module-title">${escapeHtml(module.title)}</p>
          <p class="muted">Module ID ${escapeHtml(module.id)}</p>
          ${module.sections.map((section) => renderSection(section, module.id)).join("")}
        </section>
      `,
    )
    .join("");

  document.querySelectorAll("[data-kind]").forEach((button) => {
    button.addEventListener("click", () => loadDetail(button.dataset.kind, button.dataset.id));
  });

  document.querySelectorAll("[data-module-id]").forEach((button) => {
    button.addEventListener("click", () => {
      $("#sectionModuleIdInput").value = button.dataset.moduleId;
    });
  });

  document.querySelectorAll("[data-section-id]").forEach((button) => {
    button.addEventListener("click", () => {
      $("#lectureSectionIdInput").value = button.dataset.sectionId;
    });
  });
}

function renderSection(section, moduleId) {
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
      <p class="muted">Section ID ${escapeHtml(section.id)}</p>
      <div class="list">
        <button class="item-button" type="button" data-module-id="${moduleId}">Use module for new section</button>
        <button class="item-button" type="button" data-section-id="${section.id}">Use section for new lecture</button>
        ${lectures}${questions}${tasks}${codeTasks}
      </div>
    </div>
  `;
}

function nodeButton(kind, id, title, label) {
  return `
    <button class="item-button" type="button" data-kind="${kind}" data-id="${id}">
      <strong>${escapeHtml(title)}</strong>
      <span>${escapeHtml(label)}</span>
      <span>ID ${escapeHtml(id)}</span>
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

async function submitAdmin(path, body) {
  if (!state.accessToken) {
    $("#studioResult").textContent = "Sign in as author or admin.";
    return null;
  }
  try {
    const result = await request(path, { method: "POST", body: JSON.stringify(body) });
    $("#studioResult").textContent = JSON.stringify(result, null, 2);
    await loadCourses();
    return result;
  } catch (error) {
    $("#studioResult").textContent = error.message;
    return null;
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
    await loadMe();
    setStatus("Signed in");
  } catch (error) {
    setStatus(error.message);
  }
}

function logout() {
  state.accessToken = "";
  state.refreshToken = "";
  state.currentUser = null;
  localStorage.removeItem("perminof.accessToken");
  localStorage.removeItem("perminof.refreshToken");
  setTokenStatus();
  setStatus("Signed out");
}

function bindAdminForms() {
  $("#createCourseForm").addEventListener("submit", async (event) => {
    event.preventDefault();
    await submitAdmin("/api/admin/courses", {
      title: $("#courseTitleInput").value,
      description: $("#courseDescriptionInput").value,
    });
  });

  $("#createModuleForm").addEventListener("submit", async (event) => {
    event.preventDefault();
    await submitAdmin(`/api/admin/courses/${$("#moduleCourseIdInput").value}/modules`, {
      title: $("#moduleTitleInput").value,
      description: $("#moduleDescriptionInput").value,
      position: Number($("#modulePositionInput").value),
    });
  });

  $("#createSectionForm").addEventListener("submit", async (event) => {
    event.preventDefault();
    await submitAdmin(`/api/admin/modules/${$("#sectionModuleIdInput").value}/sections`, {
      title: $("#sectionTitleInput").value,
      description: $("#sectionDescriptionInput").value,
      position: Number($("#sectionPositionInput").value),
    });
  });

  $("#createLectureForm").addEventListener("submit", async (event) => {
    event.preventDefault();
    await submitAdmin(`/api/admin/sections/${$("#lectureSectionIdInput").value}/lectures`, {
      title: $("#lectureTitleInput").value,
      content: $("#lectureContentInput").value,
      position: Number($("#lecturePositionInput").value),
    });
  });
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
$("#studioRefresh").addEventListener("click", loadCourses);
$("#workspaceTab").addEventListener("click", () => switchView("workspace"));
$("#studioTab").addEventListener("click", () => switchView("studio"));

bindAdminForms();
loadMe();
setTokenStatus();
loadCourses();
