from node:22-alpine
workdir /app
copy package*.json .
run npm install
copy . .
cmd ["npm", "run", "dev"]