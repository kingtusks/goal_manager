import { useState, useEffect } from 'react';
import { fetchGoals, createGoal, deleteGoal, makePlan, executePlan, reflectOnResult } from './api';
import './app.css';

function App() {
  const [goals, setGoals] = useState([]);
  const [newGoal, setNewGoal] = useState('');
  const [agentResult, setAgentResult] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchGoals()
      .then(data => setGoals(data))
      .catch(error => console.error('Error:', error));
  }, []);

  const addGoal = () => {
    if (!newGoal.trim()) return;
    
    createGoal(newGoal)
      .then(() => {
        setNewGoal('');
        return fetchGoals();
      })
      .then(data => setGoals(data))
      .catch(error => console.error('Error:', error));
  };

  const handleDelete = (id) => {
    deleteGoal(id)
    .then(() => fetchGoals())
    .then(data => setGoals(data))
    .catch(error => console.error('Error:', error));
  };

  const runAgents = async (goalText) => {
    setLoading(true);
    setAgentResult('');
    
    try {
      setAgentResult('Planning...');
      const planResult = await makePlan(goalText);
      console.log('Plan:', planResult);
      
      setAgentResult('Executing plan...');
      const executeResult = await executePlan(planResult.result);
      console.log('Execution:', executeResult);
      
      setAgentResult('Reflecting...');
      const reflection = await reflectOnResult(executeResult.result);
      console.log('Reflection:', reflection);
      
      setAgentResult(`Done! Reflection: ${reflection.result}`);
    } catch (error) {
      console.error('Agent error:', error);
      setAgentResult(`Error: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className='container'>
      <h1>My Goals</h1>
      
      <div>
        <input 
          type="text"
          value={newGoal}
          onChange={(e) => setNewGoal(e.target.value)}
          placeholder="Enter a goal"
          className='input'
        />
        <button onClick={addGoal} className='addGoalButton'>
          Add Goal
        </button>
      </div>

      <div>
        {goals.length > 0 && goals
        .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))  // Changed from date to created_at
        .map((goal) => {
          return (
          <div key={goal.id} className='goalContainer'>
            <h3>{goal.goal}</h3>
            <button onClick={() => runAgents(goal.goal)} disabled={loading}>
              Run Agents
            </button>
            <button onClick={() => handleDelete(goal.id)}>Delete</button>
          </div>
          )
        })}
      </div>

      {agentResult && (
        <div className='agentResult'>
          <h3>Agent Status:</h3>
          <p>{agentResult}</p>
        </div>
      )}

    </div>
  );
}

export default App;