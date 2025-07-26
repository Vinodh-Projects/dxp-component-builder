# AEM Deployment Integration Demo

## Quick Start Guide

### 1. Start the Backend Server

```bash
cd backend
python main.py
```

The backend should start on `http://localhost:8000`

### 2. Start the Frontend

```bash
cd frontend
npm install  # if not already done
npm start
```

The frontend should start on `http://localhost:3000`

### 3. Demo the Integration

#### Step 1: Generate a Component
1. Open the frontend in your browser
2. Enter a component description (e.g., "Create a hero banner component with title and CTA button")
3. Click "Generate Component"
4. Wait for the component to be generated and organized

#### Step 2: Test the Build Button
1. In the right panel, click the green "Build" button
2. Watch the notification system show build progress
3. Check the notification for build results

#### Step 3: Test the Deploy Button
1. Ensure AEM Author is running on `http://localhost:4502`
2. Click the blue "Deploy" button in the right panel
3. The deployment modal will open showing:
   - AEM server connectivity status
   - Deployment progress in real-time
   - Build and deployment logs
   - Final deployment results

#### Step 4: Monitor Results
1. Watch the deployment logs in the modal
2. Check the notifications for completion status
3. If successful, click "View in AEM" to open AEM Author
4. Navigate to `/content/dam/mysite/components` to see deployed components

## Demo Features Showcase

### 🎯 **Deploy Button Integration**
- Located in the right panel CodeDisplay component
- Opens comprehensive deployment modal
- Non-blocking operation with real-time updates

### 📱 **Deployment Modal Features**
- Real-time server connectivity check
- Deployment progress tracking
- Live build and deployment logs
- Package deployment status
- Duration tracking for build and deploy phases

### 🔔 **Smart Notifications**
- Build status notifications
- Deployment completion alerts
- Error notifications with details
- Success notifications with direct AEM links
- Auto-dismissing with appropriate durations

### 🔧 **Build Integration**
- Direct Maven module building
- UI.apps module targeting for components
- Real-time build status feedback
- Error reporting with Maven logs

## Testing the Integration

### Manual Testing Checklist

- [ ] Backend server starts successfully
- [ ] Frontend connects to backend APIs
- [ ] Component generation works
- [ ] Build button triggers module build
- [ ] Deploy button opens deployment modal
- [ ] Server status check works
- [ ] Deployment starts and progresses
- [ ] Status polling updates modal
- [ ] Notifications appear for all events
- [ ] Successful deployment shows AEM link
- [ ] Error conditions are handled gracefully

### API Testing

Use the provided test script:

```bash
cd backend
python test_frontend_integration.py
```

This will verify all API endpoints work correctly.

## Demo Script for Presentation

### Introduction (30 seconds)
"Today I'll demonstrate the complete AEM component deployment integration. We've connected the frontend Deploy button directly to our AEM deployment service, providing a seamless developer experience."

### Component Generation (1 minute)
1. Show the chat interface
2. Enter: "Create a responsive image gallery component with lightbox functionality"
3. Explain the AI processing and component generation
4. Show the generated code in the right panel

### Build Process (30 seconds)
1. Click the "Build" button
2. Show the notification system
3. Explain Maven module building
4. Show build completion notification

### Deployment Process (2 minutes)
1. Click the "Deploy" button
2. Show the deployment modal opening
3. Explain server connectivity check
4. Show real-time deployment progress
5. Point out the logs and status updates
6. Show successful completion
7. Click "View in AEM" if successful

### Error Handling (1 minute)
1. Stop AEM server (if demonstrating errors)
2. Try deployment again
3. Show error handling and notifications
4. Explain troubleshooting features

### Conclusion (30 seconds)
"This integration provides developers with a complete CI/CD-like experience, from component generation to AEM deployment, all within a single interface."

## Troubleshooting During Demo

### If Backend Won't Start
- Check Python version (3.8+)
- Install requirements: `pip install -r requirements.txt`
- Check port 8000 is available

### If Frontend Won't Start
- Check Node.js version (14+)
- Run `npm install` first
- Check port 3000 is available

### If AEM Connection Fails
- Ensure AEM Author is running on port 4502
- Check username/password in .env file
- Verify firewall settings

### If Deployment Fails
- Check Maven is installed and in PATH
- Verify project structure exists
- Check AEM server accessibility
- Review backend logs for specific errors

## Demo Environment Setup

### Required Software
- Python 3.8+
- Node.js 14+
- Maven 3.6+
- AEM Author instance (optional for full demo)

### Quick Setup Commands
```bash
# Backend setup
cd backend
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your AEM settings

# Frontend setup
cd frontend
npm install

# Start both services
# Terminal 1:
cd backend && python main.py

# Terminal 2:
cd frontend && npm start
```

### Demo Data
The system includes sample components and test data for demonstration purposes. No additional setup required for basic functionality showcase.

## Advanced Demo Features

### Component Organization
- Show AI subfolder organization (wkndai)
- Explain project structure maintenance
- Demonstrate file organization

### Real-time Updates
- Show deployment polling mechanism
- Explain status tracking
- Demonstrate progress indicators

### Error Recovery
- Show error handling workflows
- Demonstrate retry mechanisms
- Explain troubleshooting features

### Integration Points
- Explain API architecture
- Show data flow between components
- Demonstrate state management
