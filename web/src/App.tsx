import React from "react";

import "markdown-retro/css/retro.css";
import { BrowserRouter as Router, Switch, Route, Link } from "react-router-dom";
import Chronological from "./pages/Chronological";
import Lucky from "./pages/Lucky";

function App() {
  return (
    <Router>
      <Link to="/"> Timeline</Link> &nbsp;
      <Link to="/lucky">I feel lucky </Link>
      <Switch>
        <Route exact path="/">
          <Chronological />
        </Route>
        <Route exact path="/lucky">
          <Lucky />
        </Route>
      </Switch>
    </Router>
  );
}

export default App;
