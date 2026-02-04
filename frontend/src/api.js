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
      goal, 
      created_at: new Date().toISOString() 
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

export const makePlan = async (goal) => {
  const response = await fetch(`${API_URL}/agent/plan`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ goal })
  });
  return response.json();
};

export const executePlan = async (plan) => {
  const response = await fetch(`${API_URL}/agent/execute`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ plan })
  });
  return response.json();
};

export const reflectOnResult = async (result) => {
  const response = await fetch(`${API_URL}/agent/reflect`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ result })
  });
  return response.json();
};