import { useState, useEffect } from 'react';
import { 
  fetchGoals, 
  createGoal, 
  deleteGoal, 
  createPlanForGoal, 
  executeNextTask, 
  reflectOnTask 
} from './api';
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

  const runAgents = async (goalId) => {
    setLoading(true);
    setAgentResult('');
    try {
      setAgentResult('Creating plan and tasks');
      const planResult = await createPlanForGoal(goalId);
      console.log('Plan created:', planResult);
      setAgentResult(`Created ${planResult.tasks_created} tasks`);
      
      for (let i = 0; i < planResult.tasks_created; i++) {
        setAgentResult(`Executing task #${i + 1}/${planResult.tasks_created}`);
        const executeResult = await executeNextTask();
        console.log('Execution result:', executeResult);
        
        if (executeResult.message === "No pending tasks") {
          break;
        }
        
        setAgentResult(`Reflecting on task #${i + 1}.`);
        const reflection = await reflectOnTask(executeResult.task_id);
        console.log('Reflection:', reflection);
      }
      
      setAgentResult('All tasks completed');
    } catch (error) {
      console.error('Agent error:', error);
      setAgentResult(`Error: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className='container'>
      <h1>Goals</h1>
      
      <div>
        <input 
          type="text"
          value={newGoal}
          onChange={(e) => setNewGoal(e.target.value)}
          onKeyUp={(e) => e.key === 'Enter' && addGoal()}
          placeholder="Enter a goal"
          className='input'
        />
        <button onClick={addGoal} className='addGoalButton'>
          Add Goal
        </button>
      </div>

      <div>
        {goals.length > 0 && goals
          .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
          .map((goal) => {
            return (
              <div key={goal.id} className='goalContainer'>
                <h3 className="goal">{goal.goal}</h3>
                <button 
                  onClick={() => runAgents(goal.id)} 
                  disabled={loading}
                  className='runAgentsButton'
                >
                  {loading ? 'Running' : 'Run Agents'}
                </button>
                <button 
                  onClick={() => handleDelete(goal.id)}
                  className='deleteButton'
                >
                  Delete
                </button>
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