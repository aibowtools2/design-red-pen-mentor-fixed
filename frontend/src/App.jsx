import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Home from './Home';
import Upgrade from './Upgrade';
import './App.css';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/upgrade" element={<Upgrade />} />
      </Routes>
    </Router>
  );
}

export default App;
