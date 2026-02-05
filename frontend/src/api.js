const API_URL = 'http://localhost:8000';

export const fetchGoals = async () => {
  const response = await fetch(`${API_URL}/goals`);
  return response.json();
};

export const createGoal = async (goal) => {
  const response = await fetch(`${API_URL}/creategoal`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ 
      user_id: 1,  
      goal
    })
  });
  return response.json();
};

export const deleteGoal = async (id) => {
  const response = await fetch(`${API_URL}/deletegoal?id=${id}`, {
    method: 'DELETE'
  });
  return response.json();
};

export const createPlanForGoal = async (goalId) => {
  const response = await fetch(`${API_URL}/agent/plan/goal/${goalId}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' }
  });
  return response.json();
};

export const executeNextTask = async () => {
  const response = await fetch(`${API_URL}/agent/execute/task`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' }
  });
  return response.json();
};

export const reflectOnTask = async (taskId) => {
  const response = await fetch(`${API_URL}/agent/reflect/task/${taskId}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' }
  });
  return response.json();
};