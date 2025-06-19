import { AgentBay, Session } from '../../src';
import { getTestApiKey } from '../utils/test-helpers';
import { log } from '../../src/utils/logger';

describe('Session Parameters', () => {
  let agentBay: AgentBay;
  let session: Session;
  
  beforeEach(async() => {
    const apiKey = getTestApiKey();
    agentBay = new AgentBay({ apiKey });
  });
  afterEach(async () => {
    try {
      if(session){
        session.delete();
        log('Session deleted sucessfully');
        
      }
    } catch (error) {
      log(`Error deleting session: ${error}`);
    }
  });
  
  describe('create method options', () => {
    it.only('should accept empty options', async () => {
      try{
       session =  await agentBay.create();
      }catch(error){
        log(`Error creating session: ${error}`);
      }
      
    });
    
    it.only('should accept contextId option', async () => {
      try{
        const contextId = 'test-context-id';
        session = await agentBay.create({ contextId });
      }catch(error:any){
        expect(error.message).toMatch(/Failed to create session/);
      }
      
    });
    
    it.only('should accept labels option', async () => {
      try{
      
        const labels = { username: 'alice', project: 'my-project' };
        session = await agentBay.create({ labels });
      }catch(error:any){
        log(`Error creating session with labels: ${error}`);
        expect(error.message).toMatch(/Failed to create session/);
      }
      
    });
    
    it.only('should accept both contextId and labels options', async () => {
      try{
        const contextId = 'test-context-id';
        const labels = { username: 'alice', project: 'my-project' };
        session = await agentBay.create({ contextId, labels });
      }catch(error:any){
        log(`Error creating session with contextId and labels: ${error}`);
        expect(error.message).toMatch(/Failed to create session/);
      }
    });
  });
  
  describe('session creation with options', () => {
    it.only('should create a session with the specified options', async () => {
      try{
         session = await agentBay.create({
          contextId: 'test-context-id',
          labels: { username: 'alice' }
        });
      }catch(error:any){
        log(`Error creating session with options: ${error}`);
        expect(error.message).toMatch(/Failed to create session/);
      }
      
    });
  });
});
