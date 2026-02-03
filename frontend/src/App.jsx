import { useState, useEffect } from 'react';
import { fetchGoals, createGoal } from './api';

function App() {
  const [goals, setGoals] = useState([]);
  const [newGoal, setNewGoal] = useState('');

  useEffect(() => {
    fetchGoals()
      .then(data => setGoals(data))
      .catch(error => console.error('Error:', error));
  }, []);

  const addGoal = () => {
    createGoal(newGoal) //sends the goal to backend (logic in .js)
      .then(() => {
        setNewGoal(''); //clears the input
        return fetchGoals(); //fetches the goals again (to include new one)
      })
      .then(data => setGoals(data)) //updates the list
      .catch(error => console.error('Error:', error));
  };

  return (
    <div style={{ padding: '20px' }}>
      <h1>My Goals</h1>
      
      <div>
        <input 
          type="text"
          value={newGoal} //goal you put in
          onChange={(e) => setNewGoal(e.target.value)}
          placeholder="Enter a goal"
          style={{ padding: '10px', width: '300px' }}
        />
        <button onClick={addGoal} style={{ padding: '10px', marginLeft: '10px' }}>
          Add Goal
        </button>
      </div>

      <pre>{JSON.stringify(goals, null, 2)}</pre>
    </div>
  );
}

export default App;