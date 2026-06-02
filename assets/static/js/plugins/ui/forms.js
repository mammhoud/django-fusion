/**
 * @file plugins/ui/forms.js
 * Form plugins — re-exports all form handlers for use as plugins
 */
export { FormsManager }                                   from '../../modules/forms/formsManager.js';
export { UnifiedFormHandler, UnifiedFormHandler as FormHandler } from '../../modules/forms/formHandler.js';
export { AuthFormsHandler }                               from '../../modules/forms/authHandler.js';
export { ContactFormHandler }                             from '../../modules/forms/contactHandler.js';
export { ValidationUtils }                                from '../../modules/forms/validationUtils.js';
export { default as FormHandlers }                        from '../../modules/forms/index.js';
