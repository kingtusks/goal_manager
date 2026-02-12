import { useState, useEffect } from 'react';
import { 
  fetchGoals, 
  createGoal, 
  deleteGoal, 
  createPlanForGoal, 
  executeNextTask, 
  reflectOnTask,
  replanNextTask
} from './api';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faPlus, faAnchor, faPlay, faTrash, faSpinner } from '@fortawesome/free-solid-svg-icons'
import './App.css';


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

      let stepCount = 1;

      while (true) {
        setAgentResult(`Executing task ${stepCount}`);
        const executeResult = await executeNextTask();
        console.log(executeResult);

        if (executeResult.message === "No pending tasks") {
          break;
        }

        setAgentResult(`Creating material for task ${stepCount}`);
        const construct = await constructFromTask();
        console.log(construct);

        setAgentResult(`Reflecting on task ${stepCount}`);
        const reflection = await reflectOnTask(executeResult.task_id);
        console.log(reflection);

        setAgentResult(`Replanning after task ${stepCount}`);
        const decision = await replanNextTask(executeResult.task_id);
        console.log(decision);

        stepCount++;
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
      <div className='leftAlign'>
        <div className='hAlign logo'>
          <FontAwesomeIcon icon={faAnchor} className='anchorIcon'/>
          <p>anchor</p>
        </div>
        <div className='goalListContainer'>
        {goals.length > 0 && goals
          .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
          .map((goal) => {  
            return (
              <div key={goal.id} className='goalContainer'>
                <p className="goal">{goal.goal}</p>
                <div className='buttonContainer'>
                  <button 
                    onClick={() => runAgents(goal.id)} 
                    disabled={loading}
                    className='runAgentsButton'
                  >
                    {loading ? <FontAwesomeIcon icon={faSpinner}/> : <FontAwesomeIcon icon={faPlay}/>}
                  </button>
                  <button 
                    onClick={() => handleDelete(goal.id)}
                    className='deleteButton'
                  >
                    <FontAwesomeIcon icon={faTrash}/>
                  </button>
                </div>
              </div>
            )
          })}
      </div>
      </div>
      <div className='rightAlign'>
        {agentResult && (
        <div className='agentResult'>
          <h3>Agent Status</h3>
          <p>{agentResult}</p>
        </div>
        )}
        <div className='goalInputContainer'>
          <div className='hAlign inputSection'>
            <input 
              type="text"
              value={newGoal}
              onChange={(e) => setNewGoal(e.target.value)}
              onKeyUp={(e) => e.key === 'Enter' && addGoal()}
              placeholder="Enter a goal"
              className='input'
            />
            <button onClick={addGoal} className='addGoalButton'><FontAwesomeIcon icon={faPlus} className='plusIcon'/></button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;