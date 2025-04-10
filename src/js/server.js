const express = require('express');
const path = require('path');
const app = express();
const port = 3001;

app.use(express.static(path.join(__dirname, '../../views/html')));
app.use('/css', express.static(path.join(__dirname, '../../views/css')));
app.use('/js', express.static(path.join(__dirname, '.')));

app.listen(port, () => {
  console.log(`Server started on port ${port}`);
});
