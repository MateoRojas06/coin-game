const COIN_LABELS = {
    0: "cara",
    1: "sello"
};

const streakEl = document.getElementById("streak");
const statusEl = document.getElementById("status");
const saveForm = document.getElementById("save-form");
const ranking = document.getElementById("ranking");
const usernameInput = document.getElementById("username");
const guessButtons = document.querySelectorAll(".guess-btn");

function setButtonsDisabled(disabled) {
  guessButtons.forEach((btn) => {
    btn.disabled = disabled;
  });
}

function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

async function play(guess) {
  saveForm.hidden = true;
  setButtonsDisabled(true);

  try {
    const res = await fetch("/flip", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ guess }),
    });

    if (!res.ok) {
      statusEl.textContent = "Error al procesar el lanzamiento.";
      return;
    }

    const data = await res.json();
    const label = COIN_LABELS[data.result];

    if (data.win) {
      streakEl.textContent = data.streak;
      statusEl.textContent = `Salió ${label}. ¡Acertaste!`;
    } else {
      streakEl.textContent = 0;
      statusEl.textContent = `Salió ${label}. Fin de la racha (${data.final_streak}).`;
      if (data.final_streak > 0) {
        saveForm.hidden = false;
        usernameInput.focus();
      }
    }
  } finally {
    setButtonsDisabled(false);
  }
}

async function saveScore(event) {
  event.preventDefault();
  const username = usernameInput.value.trim();
  if (!username) return;

  const res = await fetch("/save-score", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username }),
  });

  if (res.ok) {
    usernameInput.value = "";
    saveForm.hidden = true;
    await loadLeaderboard();
  }
}

async function loadLeaderboard() {
    const res = await fetch("/leaderboard");
    if (!res.ok) return;

    const rows = await res.json();

    ranking.innerHTML = rows
        .map(
      (row, index) => `
        <tr>
          <td>${index + 1}</td>
          <td>${escapeHtml(row.username)}</td>
          <td>${row.streak}</td>
        </tr>
      `
    )
    .join("");
}

guessButtons.forEach((btn) => {
  btn.addEventListener("click", () => {
    const guess = Number(btn.dataset.guess);
    play(guess);
  });
});

saveForm.addEventListener("submit", saveScore);

loadLeaderboard();
