import { useState, useEffect } from 'react';
import { fetchGoals, createGoal, deleteGoal } from './api';
import './app.css';

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

  const handleDelete = (id) => {
    deleteGoal(id)
    .then(() => fetchGoals())
    .then(data => setGoals(data))
    .catch(error => console.error('Error:', error));
  };

  return (
    <div className='container'>
      <h1>My Goals</h1>
      
      <div>
        <input 
          type="text"
          value={newGoal} //goal you put in
          onChange={(e) => setNewGoal(e.target.value)}
          placeholder="Enter a goal"
          className='input'
        />
        <button onClick={addGoal} className='addGoalButton'>
          Add Goal
        </button>
      </div>

      <div>
        {goals
        .sort((a, b) => new Date(b.date) - new Date(a.date))
        .map((goal) => { //should be a good example of map
          return (
          <div key={goal.id} className='goalContainer'>
            <h3>{goal.goal}</h3>
            <button onClick={() => handleDelete(goal.id)}>Delete</button>
          </div>
        )})}
      </div>

    </div>
  );
}

export default App;