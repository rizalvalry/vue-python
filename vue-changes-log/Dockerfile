# Use an official Node.js runtime as a parent image
FROM node:16

# Set the working directory in the container
WORKDIR /app

# Copy the package.json and package-lock.json files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of your application code to the container
COPY . .

# Build the Vue.js application for production
RUN npm run build

# Expose port 5001
EXPOSE 5001

# Start the Vue.js application in production mode
CMD ["npm", "run", "serve"]
