import { FormsManager } from './formsManager.js';
import { UnifiedFormHandler } from './formHandler.js';
import { AuthFormsHandler } from './authHandler.js';
import { ContactFormHandler } from './contactHandler.js';

// ==================== GLOBAL EXPORT ====================

const FormHandler = {
    FormHandler: UnifiedFormHandler,
    AuthFormsHandler,
    ContactFormHandler,
    init: (formId, options = {}) => {
        //  if page has form 
        return new UnifiedFormHandler(formId, options);
    },
    
    initAuth: (formId, options = {}) => {
        //     update to use from auth froms handler isAuthPage 

        return new AuthFormsHandler(formId, options);
    },
    
    initContact: (formId, options = {}) => {
                //     update to use from contact froms handler hasContactForm 

        return new ContactFormHandler(formId, options);
    },
    
    createManager: (options = {}) => {
        return new FormsManager(options);
    },
    
};

// Make available globally
if (typeof window !== 'undefined') {
    window.FormsManager = FormsManager;
    window.FormsManagerService = FormsManager; // Alias for backward compatibility
    window.FormHandler = FormHandler;
}

export {
    FormsManager as UnifiedFormsManager,
    FormsManager,
    UnifiedFormHandler,
    AuthFormsHandler,
    ContactFormHandler,
    FormHandler as default
};