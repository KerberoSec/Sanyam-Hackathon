// API Helper
function getToken() {
    return localStorage.getItem('token');
}

function getAuthHeader() {
    return {
        'Authorization': `Bearer ${getToken()}`,
        'Content-Type': 'application/json'
    };
}

async function apiCall(endpoint, method = 'GET', data = null) {
    const options = {
        method,
        headers: getAuthHeader()
    };

    if (data && method !== 'GET') {
        options.body = JSON.stringify(data);
    }

    try {
        const response = await fetch(endpoint, options);

        if (response.status === 401) {
            localStorage.removeItem('token');
            window.location.href = '/login';
            return null;
        }

        return await response.json();
    } catch (error) {
        console.error('Error:', error);
        return null;
    }
}

// Check authentication
function checkAuth() {
    if (!getToken()) {
        window.location.href = '/login';
    }
}

// Initialize Dashboard
async function initDashboard() {
    checkAuth();

    const user = JSON.parse(localStorage.getItem('user') || '{}');
    document.getElementById('userName').textContent = user.name || 'User';

    // Load data
    await loadUserStats();
    await loadHabits();
    await loadMood();
    await loadAnalytics();
    await loadBadges();
    await loadCoachMessage();
}

// Load User Stats
async function loadUserStats() {
    const response = await apiCall('/api/analytics');
    if (!response) return;

    const summary = response.summary;
    document.getElementById('streakDays').textContent = summary.combined_streak;
    document.getElementById('totalCompletions').textContent = summary.total_completions;
    document.getElementById('consistency').textContent = summary.consistency_score + '%';
    document.getElementById('totalHabits').textContent = summary.total_habits;

    // Update user level and XP
    document.getElementById('userLevel').textContent = `Lvl ${response.user_level}`;
    document.getElementById('userXP').textContent = `${response.user_xp} XP`;
}

// Load Habits
async function loadHabits() {
    const response = await apiCall('/api/habits');
    if (!response) return;

    const habitsList = document.getElementById('habitsList');

    if (response.habits.length === 0) {
        habitsList.innerHTML = `
            <div class="text-center py-5 text-muted">
                <p>Create your first habit to get started!</p>
            </div>
        `;
        return;
    }

    habitsList.innerHTML = response.habits.map(habit => `
        <div class="habit-item ${habit.today_status || 'missed'}" id="habit-${habit.id}">
            <div class="habit-icon">${habit.icon}</div>
            <div class="habit-content">
                <div class="habit-title">${habit.title}</div>
                <div class="habit-streak">
                    ${habit.current_streak > 0 ? `<span class="habit-stream">🔥 ${habit.current_streak} day streak</span>` : '<span class="text-danger">Streak broken</span>'}
                </div>
                <div class="text-muted small">
                    ${habit.total_completions} completions • ${habit.consistency_score}% consistency
                </div>
            </div>
            <div class="habit-actions">
                ${habit.today_status !== 'completed' ? `<button class="habit-btn btn-complete" onclick="completeHabit(${habit.id})">Complete</button>` : '<span class="badge bg-success">✓ Done</span>'}
                ${habit.today_status !== 'skipped' ? `<button class="habit-btn btn-skip" onclick="skipHabit(${habit.id})">Skip</button>` : ''}
            </div>
        </div>
    `).join('');
}

// Complete Habit
async function completeHabit(habitId) {
    const response = await apiCall(`/api/habits/${habitId}/complete`, 'POST');
    if (!response) return;

    // Celebration animations and feedback
    confetti({
        particleCount: 100,
        spread: 70,
        origin: { y: 0.6 }
    });

    showToast(`${response.xp_earned} XP earned! 🎉`, 'success');

    // Show streak message if available
    if (response.streak_message) {
        showToast(response.streak_message, 'info');
    }

    // Show badge notifications
    if (response.badges_unlocked && response.badges_unlocked.length > 0) {
        response.badges_unlocked.forEach(badge => {
            showToast(`New Badge: ${badge.icon} ${badge.name}!`, 'success');
        });
    }

    // Reload data
    await loadHabits();
    await loadUserStats();
    await loadBadges();
}

// Skip Habit
async function skipHabit(habitId) {
    const response = await apiCall(`/api/habits/${habitId}/skip`, 'POST');
    if (!response) return;

    showToast('Habit skipped. No worries, keep going!', 'info');
    await loadHabits();
    await loadUserStats();
}

// Miss Habit
async function missHabit(habitId) {
    const response = await apiCall(`/api/habits/${habitId}/miss`, 'POST');
    if (!response) return;

    showToast('Marked as missed. Get back on track tomorrow!', 'warning');
    await loadHabits();
    await loadUserStats();
}

// Load Mood
async function loadMood() {
    const response = await apiCall('/api/mood/today');
    if (!response) return;

    if (response.mood) {
        document.querySelector(`[onclick="logMood('${response.mood.mood}')"]`).classList.add('selected');
    }
}

// Log Mood
async function logMood(mood) {
    const response = await apiCall('/api/mood', 'POST', { mood });
    if (!response) return;

    // Update UI
    document.querySelectorAll('.mood-option').forEach(el => el.classList.remove('selected'));
    document.querySelector(`[onclick="logMood('${mood}')"]`).classList.add('selected');

    const feedbackEl = document.getElementById('moodFeedback');
    const messages = {
        happy: "That's wonderful! Keep spreading positive vibes!",
        neutral: "That's okay. Take care of yourself today.",
        sad: "We're here for you. Consider talking to someone you trust."
    };

    feedbackEl.textContent = messages[mood];
    feedbackEl.style.opacity = '0';
    setTimeout(() => { feedbackEl.style.opacity = '1'; }, 0);
}

// Load Analytics
async function loadAnalytics() {
    const response = await apiCall('/api/analytics');
    if (!response) return;

    // Weekly Chart
    const weeklyCtx = document.getElementById('completionChart');
    if (weeklyCtx) {
        new Chart(weeklyCtx, {
            type: 'bar',
            data: {
                labels: response.weekly_chart.map(d => d.day.substring(0, 3)),
                datasets: [{
                    label: 'Completions',
                    data: response.weekly_chart.map(d => d.completed),
                    backgroundColor: '#667eea',
                    borderRadius: 8
                }, {
                    label: 'Skipped',
                    data: response.weekly_chart.map(d => d.skipped),
                    backgroundColor: '#e5e7eb',
                    borderRadius: 8
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        display: true
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }

    // Mood Chart
    const moodCtx = document.getElementById('moodChart');
    if (moodCtx) {
        const moodResponse = await apiCall('/api/mood/analytics');
        if (moodResponse && moodResponse.mood_distribution) {
            new Chart(moodCtx, {
                type: 'doughnut',
                data: {
                    labels: ['Happy', 'Neutral', 'Sad'],
                    datasets: [{
                        data: [
                            moodResponse.mood_distribution.happy,
                            moodResponse.mood_distribution.neutral,
                            moodResponse.mood_distribution.sad
                        ],
                        backgroundColor: ['#10b981', '#f59e0b', '#ef4444'],
                        borderRadius: 8
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    plugins: {
                        legend: {
                            position: 'bottom'
                        }
                    }
                }
            });
        }
    }
}

// Load Badges
async function loadBadges() {
    const response = await apiCall('/api/auth/me');
    if (!response) return;

    const badgesContainer = document.getElementById('badgesList');

    const badges = [
        { name: 'First Week', icon: '🔥' },
        { name: 'Two Weeks Strong', icon: '💪' },
        { name: 'Monthly Master', icon: '👑' },
        { name: 'Centennial', icon: '💯' },
        { name: 'Yearly Champion', icon: '🎯' },
        { name: 'Getting Started', icon: '🚀' },
        { name: 'Habit Builder', icon: '🏗️' },
        { name: 'Consistency King', icon: '👑' }
    ];

    badgesContainer.innerHTML = badges.map(badge => `
        <div class="badge-item" title="${badge.name}">
            <div class="badge-icon">${badge.icon}</div>
            <div class="badge-name">${badge.name}</div>
        </div>
    `).join('');
}

// Load Coach Message
async function loadCoachMessage() {
    const response = await apiCall('/api/analytics');
    if (!response) return;

    const coachEl = document.getElementById('coachMessage');
    const coachTextEl = document.getElementById('coachText');

    if (response.insights && response.insights.length > 0) {
        const insight = response.insights[0];
        coachTextEl.innerHTML = insight.message;
        coachEl.style.display = 'flex';
    }
}

// Create Habit
async function createHabit() {
    const title = document.getElementById('habitTitle').value;
    const category = document.getElementById('habitCategory').value;
    const icon = document.getElementById('habitIcon').value;

    const frequencyCheckboxes = document.querySelectorAll('#frequencyOptions input:checked');
    const frequency = Array.from(frequencyCheckboxes).map(cb => cb.value);

    if (!title || frequency.length === 0) {
        alert('Please fill all fields');
        return;
    }

    const response = await apiCall('/api/habits', 'POST', {
        title,
        category,
        icon,
        frequency
    });

    if (response) {
        showToast('Habit created! 🎉', 'success');
        document.getElementById('newHabitForm').reset();

        // Close modal
        bootstrap.Modal.getInstance(document.getElementById('newHabitModal')).hide();

        // Reload
        await loadHabits();
        await loadUserStats();
    }
}

// Logout
function logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    window.location.href = '/login';
}

// Dark Mode
function toggleDarkMode() {
    document.body.classList.toggle('dark-mode');
    localStorage.setItem('darkMode', document.body.classList.contains('dark-mode'));
}

// Load dark mode preference
function loadDarkMode() {
    if (localStorage.getItem('darkMode') === 'true') {
        document.body.classList.add('dark-mode');
    }
}

// Toast notifications
function showToast(message, type = 'info') {
    const toastContainer = document.createElement('div');
    toastContainer.className = `position-fixed bottom-0 end-0 p-3`;
    toastContainer.innerHTML = `
        <div class="alert alert-${type} alert-dismissible fade show" role="alert" style="min-width: 300px;">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;

    document.body.appendChild(toastContainer);

    // Auto remove after 3 seconds
    setTimeout(() => {
        toastContainer.remove();
    }, 3000);
}

// Add CSS for selected mood
const style = document.createElement('style');
style.textContent = `
    .mood-option.selected {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.2), rgba(118, 75, 162, 0.2));
        border: 2px solid var(--primary);
    }
`;
document.head.appendChild(style);

// Initialize when page loads
document.addEventListener('DOMContentLoaded', initDashboard);
