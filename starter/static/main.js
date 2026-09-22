// Client-side rendering and interaction for the Flask-backed Sudoku
const SIZE = 9;
const LEADERBOARD_KEY = 'sudokuTopScores';
const THEME_KEY = 'sudokuTheme';
let puzzle = [];
let timerInterval = null;
let elapsedSeconds = 0;
let hintsUsed = 0;
let currentDifficulty = 'medium';
let scoreSaved = false;

function applyTheme(theme) {
  const isDark = theme === 'dark';
  document.documentElement.dataset.theme = isDark ? 'dark' : 'light';
  const toggle = document.getElementById('theme-toggle');
  toggle.setAttribute('aria-pressed', String(isDark));
  toggle.innerText = isDark ? 'Light Mode' : 'Dark Mode';
}

function toggleTheme() {
  const currentTheme = document.documentElement.dataset.theme || 'light';
  const nextTheme = currentTheme === 'dark' ? 'light' : 'dark';
  applyTheme(nextTheme);
  try {
    localStorage.setItem(THEME_KEY, nextTheme);
  } catch (error) {
  }
}

function loadTheme() {
  let theme = 'light';
  try {
    theme = localStorage.getItem(THEME_KEY) || theme;
  } catch (error) {
  }
  applyTheme(theme);
}

function loadLeaderboard() {
  try {
    const records = JSON.parse(localStorage.getItem(LEADERBOARD_KEY) || '[]');
    if (!Array.isArray(records)) return [];
    return records
      .filter(record => (
        record && typeof record.name === 'string'
        && Number.isFinite(record.time)
        && typeof record.difficulty === 'string'
        && Number.isFinite(record.hints)
      ))
      .sort((first, second) => (
        first.time - second.time
        || first.hints - second.hints
        || first.createdAt - second.createdAt
      ))
      .slice(0, 10);
  } catch (error) {
    return [];
  }
}

function saveLeaderboard(records) {
  try {
    localStorage.setItem(LEADERBOARD_KEY, JSON.stringify(records));
    return true;
  } catch (error) {
    return false;
  }
}

function formatTime(totalSeconds) {
  const minutes = Math.floor(totalSeconds / 60).toString().padStart(2, '0');
  const seconds = (totalSeconds % 60).toString().padStart(2, '0');
  return `${minutes}:${seconds}`;
}

function renderLeaderboard() {
  const body = document.getElementById('leaderboard-body');
  body.innerHTML = '';
  loadLeaderboard().forEach((record, index) => {
    const row = document.createElement('tr');
    row.innerHTML = `<td>${index + 1}</td><td></td><td>${formatTime(record.time)}</td>`
      + `<td>${record.difficulty}</td><td>${record.hints}</td>`;
    row.children[1].textContent = record.name;
    body.appendChild(row);
  });
}

function showScoreForm() {
  document.getElementById('score-form').hidden = false;
  document.getElementById('score-name').focus();
}

function saveScore() {
  if (scoreSaved) return;
  const nameInput = document.getElementById('score-name');
  const name = nameInput.value.trim();
  const message = document.getElementById('message');
  if (!name) {
    message.style.color = '#d32f2f';
    message.innerText = 'Enter your name to save your score.';
    return;
  }

  const records = loadLeaderboard();
  records.push({
    name,
    time: elapsedSeconds,
    difficulty: currentDifficulty,
    hints: hintsUsed,
    createdAt: Date.now(),
  });
  records.sort((first, second) => (
    first.time - second.time
    || first.hints - second.hints
    || first.createdAt - second.createdAt
  ));
  const saved = saveLeaderboard(records.slice(0, 10));
  if (!saved) {
    message.style.color = '#d32f2f';
    message.innerText = 'Unable to save your score in this browser.';
    return;
  }
  scoreSaved = true;
  document.getElementById('score-form').hidden = true;
  message.style.color = '#388e3c';
  message.innerText = 'Score saved!';
  renderLeaderboard();
}

function updateTimer() {
  document.getElementById('timer').innerText = formatTime(elapsedSeconds);
}

function startTimer() {
  clearInterval(timerInterval);
  elapsedSeconds = 0;
  updateTimer();
  timerInterval = setInterval(() => {
    elapsedSeconds += 1;
    updateTimer();
  }, 1000);
}

function stopTimer() {
  clearInterval(timerInterval);
  timerInterval = null;
}

function createBoardElement() {
  const boardDiv = document.getElementById('sudoku-board');
  boardDiv.innerHTML = '';
  for (let i = 0; i < SIZE; i++) {
    const rowDiv = document.createElement('div');
    rowDiv.className = 'sudoku-row';
    for (let j = 0; j < SIZE; j++) {
      const input = document.createElement('input');
      input.type = 'text';
      input.maxLength = 1;
      input.className = 'sudoku-cell';
      input.dataset.row = i;
      input.dataset.col = j;
      input.addEventListener('input', (e) => {
        const val = e.target.value.replace(/[^1-9]/g, '');
        e.target.value = val;
        checkSolution();
      });
      rowDiv.appendChild(input);
    }
    boardDiv.appendChild(rowDiv);
  }
}

function renderPuzzle(puz) {
  puzzle = puz;
  createBoardElement();
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  for (let i = 0; i < SIZE; i++) {
    for (let j = 0; j < SIZE; j++) {
      const idx = i * SIZE + j;
      const val = puzzle[i][j];
      const inp = inputs[idx];
      if (val !== 0) {
        inp.value = val;
        inp.disabled = true;
        inp.className = 'sudoku-cell prefilled';
      } else {
        inp.value = '';
        inp.disabled = false;
        inp.className = 'sudoku-cell';
      }
    }
  }
}

async function newGame() {
  const difficulty = document.getElementById('difficulty').value;
  const res = await fetch(`/new?difficulty=${difficulty}`);
  const data = await res.json();
  if (data.error) {
    document.getElementById('message').innerText = data.error;
    return;
  }
  renderPuzzle(data.puzzle);
  currentDifficulty = data.difficulty;
  hintsUsed = 0;
  scoreSaved = false;
  document.getElementById('score-form').hidden = true;
  document.getElementById('score-name').value = '';
  startTimer();
  document.getElementById('message').innerText = '';
}

async function checkSolution() {
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  const board = [];
  for (let i = 0; i < SIZE; i++) {
    board[i] = [];
    for (let j = 0; j < SIZE; j++) {
      const idx = i * SIZE + j;
      const val = inputs[idx].value;
      board[i][j] = val ? parseInt(val, 10) : 0;
    }
  }
  const res = await fetch('/check', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({board})
  });
  const data = await res.json();
  const msg = document.getElementById('message');
  if (data.error) {
    msg.style.color = '#d32f2f';
    msg.innerText = data.error;
    return;
  }
  const incorrect = new Set(data.incorrect.map(x => x[0]*SIZE + x[1]));
  for (let idx = 0; idx < inputs.length; idx++) {
    const inp = inputs[idx];
    if (inp.disabled) continue;
    inp.className = 'sudoku-cell';
    if (incorrect.has(idx)) {
      inp.className = 'sudoku-cell incorrect';
    } else if (inp.value) {
      inp.className = 'sudoku-cell correct';
    }
  }
  if (data.complete) {
    stopTimer();
    msg.style.color = '#388e3c';
    msg.innerText = 'Congratulations! You solved it!';
    if (!scoreSaved) showScoreForm();
  } else if (incorrect.size > 0) {
    msg.style.color = '#d32f2f';
    msg.innerText = 'Some cells are incorrect.';
  } else {
    msg.innerText = '';
  }
}

async function requestHint() {
  const inputs = document.getElementById('sudoku-board').getElementsByTagName('input');
  const board = [];
  for (let i = 0; i < SIZE; i++) {
    board[i] = [];
    for (let j = 0; j < SIZE; j++) {
      const value = inputs[i * SIZE + j].value;
      board[i][j] = value ? parseInt(value, 10) : 0;
    }
  }

  const res = await fetch('/hint', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({board})
  });
  const data = await res.json();
  const msg = document.getElementById('message');
  if (data.error) {
    msg.style.color = '#d32f2f';
    msg.innerText = data.error;
    return;
  }

  const input = inputs[data.row * SIZE + data.col];
  input.value = data.value;
  input.disabled = true;
  input.className = 'sudoku-cell hint';
  hintsUsed += 1;
  await checkSolution();
}

// Wire buttons
window.addEventListener('load', () => {
  loadTheme();
  document.getElementById('new-game').addEventListener('click', newGame);
  document.getElementById('difficulty').addEventListener('change', newGame);
  document.getElementById('check-solution').addEventListener('click', checkSolution);
  document.getElementById('hint').addEventListener('click', requestHint);
  document.getElementById('save-score').addEventListener('click', saveScore);
  document.getElementById('theme-toggle').addEventListener('click', toggleTheme);
  renderLeaderboard();
  // initialize
  newGame();
});