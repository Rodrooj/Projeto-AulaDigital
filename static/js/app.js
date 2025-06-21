// AulaDigital JavaScript Application

// Global variables
let currentUser = null;
let authToken = null;

// API Base URL
const API_BASE_URL = '/api';

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

// Initialize application
function initializeApp() {
    checkAuthStatus();
    setupEventListeners();
    loadInitialData();
}

// Check authentication status
function checkAuthStatus() {
    const token = localStorage.getItem('authToken');
    const userData = localStorage.getItem('userData');

    if (token && userData) {
        authToken = token;
        currentUser = JSON.parse(userData);
        updateUIForLoggedInUser();
    } else {
        updateUIForLoggedOutUser();
    }
}

// Update UI for logged in user
function updateUIForLoggedInUser() {
    const userMenu = document.getElementById('user-menu');
    const loginMenu = document.getElementById('login-menu');
    const userName = document.getElementById('user-name');

    if (userMenu && loginMenu && userName) {
        userMenu.style.display = 'block';
        loginMenu.style.display = 'none';
        userName.textContent = currentUser.nome || currentUser.username;
    }
}

// Update UI for logged out user
function updateUIForLoggedOutUser() {
    const userMenu = document.getElementById('user-menu');
    const loginMenu = document.getElementById('login-menu');

    if (userMenu && loginMenu) {
        userMenu.style.display = 'none';
        loginMenu.style.display = 'block';
    }
}

// Setup event listeners
function setupEventListeners() {
    // Form submissions
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }

    const registerForm = document.getElementById('register-form');
    if (registerForm) {
        registerForm.addEventListener('submit', handleRegister);
    }

    // Search functionality
    const searchInput = document.getElementById('search-input');
    if (searchInput) {
        searchInput.addEventListener('input', debounce(handleSearch, 300));
    }
}

// Load initial data
function loadInitialData() {
    // Load data based on current page
    const currentPage = getCurrentPage();

    switch (currentPage) {
        case 'home':
            loadHomeData();
            break;
        case 'tutoriais':
            loadTutorials();
            break;
        case 'quiz':
            loadQuizData();
            break;
    }
}

// Get current page
function getCurrentPage() {
    const path = window.location.pathname;
    if (path === '/' || path === '/home/') return 'home';
    if (path.includes('tutoriais')) return 'tutoriais';
    if (path.includes('quiz')) return 'quiz';
    return 'unknown';
}

// API Helper Functions
async function apiRequest(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
        }
    };

    if (authToken) {
        defaultOptions.headers['Authorization'] = `Token ${authToken}`;
    }

    const finalOptions = { ...defaultOptions, ...options };

    try {
        const response = await fetch(url, finalOptions);

        if (response.status === 401) {
            // Token expired or invalid
            logout();
            return null;
        }

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.error('API request failed:', error);
        showAlert('Erro de conexão. Tente novamente.', 'danger');
        return null;
    }
}

// Authentication Functions
async function handleLogin(event) {
    event.preventDefault();

    const formData = new FormData(event.target);
    const loginData = {
        username: formData.get('username'),
        password: formData.get('password')
    };

    showLoading(true);

    try {
        const response = await apiRequest('/usuarios/login/', {
            method: 'POST',
            body: JSON.stringify(loginData)
        });

        if (response && response.token) {
            authToken = response.token;
            currentUser = response.user;

            localStorage.setItem('authToken', authToken);
            localStorage.setItem('userData', JSON.stringify(currentUser));

            showAlert('Login realizado com sucesso!', 'success');
            updateUIForLoggedInUser();

            // Redirect to home or intended page
            setTimeout(() => {
                window.location.href = '/';
            }, 1000);
        } else {
            showAlert('Credenciais inválidas', 'danger');
        }
    } catch (error) {
        showAlert('Erro ao fazer login', 'danger');
    } finally {
        showLoading(false);
    }
}

async function handleRegister(event) {
    event.preventDefault();

    const formData = new FormData(event.target);
    const registerData = {
        username: formData.get('username'),
        email: formData.get('email'),
        nome: formData.get('nome'),
        password: formData.get('password'),
        password_confirm: formData.get('password_confirm'),
        tipo_usuario: formData.get('tipo_usuario') || 'professor',
        matricula: formData.get('matricula')
    };

    showLoading(true);

    try {
        const response = await apiRequest('/usuarios/registro/', {
            method: 'POST',
            body: JSON.stringify(registerData)
        });

        if (response && response.user) {
            showAlert('Conta criada com sucesso! Faça login para continuar.', 'success');

            // Redirect to login page
            setTimeout(() => {
                window.location.href = '/login/';
            }, 2000);
        } else {
            showAlert('Erro ao criar conta', 'danger');
        }
    } catch (error) {
        showAlert('Erro ao criar conta', 'danger');
    } finally {
        showLoading(false);
    }
}

function logout() {
    localStorage.removeItem('authToken');
    localStorage.removeItem('userData');
    authToken = null;
    currentUser = null;

    updateUIForLoggedOutUser();
    showAlert('Logout realizado com sucesso!', 'info');

    // Redirect to home
    setTimeout(() => {
        window.location.href = '/';
    }, 1000);
}

// Tutorial Functions
async function loadTutorials(filters = {}) {
    const queryParams = new URLSearchParams(filters).toString();
    const endpoint = queryParams ? `/tutoriais/?${queryParams}` : '/tutoriais/';

    const tutorials = await apiRequest(endpoint);

    if (tutorials) {
        displayTutorials(tutorials.results || tutorials);
    }
}

function displayTutorials(tutorials) {
    const container = document.getElementById('tutorials-container');
    if (!container) return;

    container.innerHTML = '';

    if (tutorials.length === 0) {
        container.innerHTML = `
            <div class="col-12 text-center">
                <p class="text-muted">Nenhum tutorial encontrado.</p>
            </div>
        `;
        return;
    }

    tutorials.forEach(tutorial => {
        const tutorialCard = createTutorialCard(tutorial);
        container.appendChild(tutorialCard);
    });
}

function createTutorialCard(tutorial) {
    const col = document.createElement('div');
    col.className = 'col-md-6 col-lg-4 mb-4';

    const typeIcon = tutorial.tipo === 'video' ? 'fas fa-play-circle' : 'fas fa-file-alt';
    const typeColor = tutorial.tipo === 'video' ? 'text-danger' : 'text-primary';
    const typeBadge = tutorial.tipo === 'video' ? 'bg-danger' : 'bg-primary';

    col.innerHTML = `
        <div class="card h-100 tutorial-card shadow-sm border-0">
            <div class="card-body position-relative">
                <span class="badge ${typeBadge} tutorial-type-badge">
                    <i class="${typeIcon} me-1"></i>${tutorial.tipo.toUpperCase()}
                </span>
                <h5 class="card-title mt-3">${tutorial.titulo}</h5>
                <p class="card-text text-muted">${tutorial.descricao || 'Sem descrição disponível'}</p>
                <div class="d-flex justify-content-between align-items-center mt-3">
                    <small class="text-muted">
                        Por ${tutorial.criador_nome || 'AulaDigital'}
                    </small>
                    <a href="${tutorial.link_conteudo}" target="_blank" class="btn btn-outline-primary btn-sm">
                        Acessar <i class="fas fa-external-link-alt ms-1"></i>
                    </a>
                </div>
            </div>
        </div>
    `;

    return col;
}

// Quiz Functions
async function loadQuizData() {
    if (!currentUser || currentUser.tipo_usuario !== 'aluno') {
        showAlert('Apenas alunos podem jogar o quiz', 'warning');
        return;
    }

    await loadRandomQuestion();
}

async function loadRandomQuestion(difficulty = null) {
    const endpoint = difficulty ? `/perguntas/aleatoria/?dificuldade=${difficulty}` : '/perguntas/aleatoria/';
    const question = await apiRequest(endpoint);

    if (question) {
        displayQuestion(question);
    }
}

function displayQuestion(question) {
    const container = document.getElementById('question-container');
    if (!container) return;

    container.innerHTML = `
        <div class="question-card card p-4 mb-4">
            <div class="d-flex justify-content-between align-items-center mb-3">
                <span class="badge bg-info">${question.dificuldade.toUpperCase()}</span>
                <button class="btn btn-outline-secondary btn-sm" onclick="loadRandomQuestion()">
                    <i class="fas fa-sync-alt me-1"></i>Nova Pergunta
                </button>
            </div>
            <h4 class="question-text mb-4">${question.enunciado}</h4>
            <div class="answers-container">
                ${question.alternativas.map((alt, index) => `
                    <div class="answer-option" onclick="selectAnswer(${alt.id}, ${question.id})">
                        <strong>${String.fromCharCode(65 + index)})</strong> ${alt.texto_alternativa}
                    </div>
                `).join('')}
            </div>
        </div>
    `;
}

async function selectAnswer(alternativeId, questionId) {
    if (!currentUser || currentUser.tipo_usuario !== 'aluno') {
        showAlert('Apenas alunos podem responder', 'warning');
        return;
    }

    const answerData = {
        pergunta_id: questionId,
        alternativa_id: alternativeId
    };

    const result = await apiRequest('/perguntas/responder/', {
        method: 'POST',
        body: JSON.stringify(answerData)
    });

    if (result) {
        showAnswerResult(result, alternativeId);
    }
}

function showAnswerResult(result, selectedId) {
    const options = document.querySelectorAll('.answer-option');

    options.forEach(option => {
        option.style.pointerEvents = 'none';

        if (option.onclick.toString().includes(selectedId)) {
            option.classList.add(result.acertou ? 'correct' : 'incorrect');
        }

        if (option.onclick.toString().includes(result.alternativa_correta.id)) {
            option.classList.add('correct');
        }
    });

    const message = result.acertou ? 'Parabéns! Resposta correta!' : 'Resposta incorreta.';
    const alertType = result.acertou ? 'success' : 'danger';

    showAlert(`${message} ${result.explicacao}`, alertType);

    // Show next question button
    setTimeout(() => {
        const container = document.getElementById('question-container');
        const nextButton = document.createElement('div');
        nextButton.className = 'text-center mt-3';
        nextButton.innerHTML = `
            <button class="btn btn-primary" onclick="loadRandomQuestion()">
                <i class="fas fa-arrow-right me-1"></i>Próxima Pergunta
            </button>
        `;
        container.appendChild(nextButton);
    }, 2000);
}

// Utility Functions
function showAlert(message, type = 'info') {
    const alertsContainer = document.getElementById('alerts-container');
    if (!alertsContainer) return;

    const alertId = 'alert-' + Date.now();
    const alertHTML = `
        <div id="${alertId}" class="alert alert-${type} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;

    alertsContainer.insertAdjacentHTML('beforeend', alertHTML);

    // Auto-remove after 5 seconds
    setTimeout(() => {
        const alertElement = document.getElementById(alertId);
        if (alertElement) {
            alertElement.remove();
        }
    }, 5000);
}

function showLoading(show) {
    const loadingElements = document.querySelectorAll('.loading-spinner');
    const submitButtons = document.querySelectorAll('button[type="submit"]');

    if (show) {
        submitButtons.forEach(btn => {
            btn.disabled = true;
            btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Carregando...';
        });
    } else {
        submitButtons.forEach(btn => {
            btn.disabled = false;
            btn.innerHTML = btn.dataset.originalText || 'Enviar';
        });
    }
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function handleSearch(event) {
    const query = event.target.value.trim();
    const currentPage = getCurrentPage();

    if (currentPage === 'tutoriais') {
        loadTutorials({ q: query });
    }
}

// Home page specific functions
async function loadHomeData() {
    // Load recent tutorials for home page
    const tutorials = await apiRequest('/tutoriais/recentes/?limit=3');
    if (tutorials) {
        displayRecentTutorials(tutorials);
    }
}

function displayRecentTutorials(tutorials) {
    const container = document.getElementById('recent-tutorials');
    if (!container) return;

    container.innerHTML = '';

    tutorials.forEach(tutorial => {
        const tutorialCard = createTutorialCard(tutorial);
        container.appendChild(tutorialCard);
    });
}

// Export functions for global access
window.logout = logout;
window.loadRandomQuestion = loadRandomQuestion;
window.selectAnswer = selectAnswer;

