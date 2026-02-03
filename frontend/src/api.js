const API_URL = 'http://localhost:8000';

export const fetchGoals = () => { //r
  return fetch(`${API_URL}/goals`)
    .then(res => res.json());
};

export const createGoal = (goalText) => { //c
    //2 params for fetch cus one is only R while this is C (as seen w post method)
  return fetch(`${API_URL}/creategoal`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      userid: 1,
      goal: goalText,
      date: new Date().toISOString()
    })
  }).then(res => res.json());
};