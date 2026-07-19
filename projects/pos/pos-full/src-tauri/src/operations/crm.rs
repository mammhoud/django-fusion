//! CRM (Customer Relationship Management) operations for POS Full Edition.
//!
//! Provides CRUD functions for all CRM entities managed by the Rust/Diesel ORM:
//! Companies, Contacts, Pipelines, Stages, Deals, Activities, and Notes.
//!
//! These Diesel-backed tables mirror the cloud CRM Django models and are designed
//! for local-first operation — the cloud server (shared-portal/cloud/) handles remote sync.
//!
//! Change events are emitted via `crate::operations::signals` so that
//! subscribers (sidecar, cloud sync, UI) can react to modifications.
//!
//! Related Names: crm, companies, contacts, pipelines, stages, deals, activities, notes
//! Tags: #crm #diesel #operations #pos-full

use diesel::prelude::*;
use crate::db::{models::*, open_conn};
use crate::operations::signals::{self, ChangeEvent};
use std::path::PathBuf;

// ---------------------------------------------------------------------------
// Companies
// ---------------------------------------------------------------------------

pub fn get_crm_companies(db_path: &PathBuf) -> Result<Vec<CrmCompany>, String> {
    let mut conn = open_conn(db_path)?;
    use crate::db::schema::crm_companies::dsl::*;
    crm_companies
        .order(name.asc())
        .load::<CrmCompany>(&mut conn)
        .map_err(|e| e.to_string())
}

pub fn get_crm_company(db_path: &PathBuf, company_id: i32) -> Result<CrmCompany, String> {
    let mut conn = open_conn(db_path)?;
    use crate::db::schema::crm_companies::dsl::*;
    crm_companies
        .find(company_id)
        .first::<CrmCompany>(&mut conn)
        .map_err(|e| e.to_string())
}

pub fn create_crm_company(db_path: &PathBuf, data: NewCrmCompany) -> Result<CrmCompany, String> {
    let mut conn = open_conn(db_path)?;
    use crate::db::schema::crm_companies::dsl::*;
    let company = diesel::insert_into(crm_companies)
        .values(&data)
        .returning(CrmCompany::as_returning())
        .get_result(&mut conn)
        .map_err(|e| e.to_string())?;
    signals::emit(ChangeEvent::EntityChanged("crm_company".into(), company.id));
    Ok(company)
}

pub fn update_crm_company(db_path: &PathBuf, company_id: i32, data: UpdateCrmCompany) -> Result<CrmCompany, String> {
    let mut conn = open_conn(db_path)?;
    use crate::db::schema::crm_companies::dsl::*;
    let company = diesel::update(crm_companies.filter(id.eq(company_id)))
        .set(&data)
        .returning(CrmCompany::as_returning())
        .get_result(&mut conn)
        .map_err(|e| e.to_string())?;
    signals::emit(ChangeEvent::EntityChanged("crm_company".into(), company.id));
    Ok(company)
}

pub fn delete_crm_company(db_path: &PathBuf, company_id: i32) -> Result<(), String> {
    let mut conn = open_conn(db_path)?;
    use crate::db::schema::crm_companies::dsl::*;
    diesel::delete(crm_companies.filter(id.eq(company_id)))
        .execute(&mut conn)
        .map_err(|e| e.to_string())?;
    signals::emit(ChangeEvent::EntityChanged("crm_company".into(), company_id));
    Ok(())
}

// ---------------------------------------------------------------------------
// Contacts
// ---------------------------------------------------------------------------

pub fn get_crm_contact(db_path: &PathBuf, contact_id: i32) -> Result<CrmContact, String> {
    let mut conn = open_conn(db_path)?;
    use crate::db::schema::crm_contacts::dsl::*;
    crm_contacts
        .find(contact_id)
        .first::<CrmContact>(&mut conn)
        .map_err(|e| e.to_string())
}

pub fn get_crm_contacts(db_path: &PathBuf) -> Result<Vec<CrmContact>, String> {
    let mut conn = open_conn(db_path)?;
    use crate::db::schema::crm_contacts::dsl::*;
    crm_contacts
        .order((last_name.asc(), first_name.asc()))
        .load::<CrmContact>(&mut conn)
        .map_err(|e| e.to_string())
}

pub fn create_crm_contact(db_path: &PathBuf, data: NewCrmContact) -> Result<CrmContact, String> {
    let mut conn = open_conn(db_path)?;
    use crate::db::schema::crm_contacts::dsl::*;
    let contact = diesel::insert_into(crm_contacts)
        .values(&data)
        .returning(CrmContact::as_returning())
        .get_result(&mut conn)
        .map_err(|e| e.to_string())?;
    signals::emit(ChangeEvent::EntityChanged("crm_contact".into(), contact.id));
    Ok(contact)
}

pub fn update_crm_contact(db_path: &PathBuf, contact_id: i32, data: UpdateCrmContact) -> Result<CrmContact, String> {
    let mut conn = open_conn(db_path)?;
    use crate::db::schema::crm_contacts::dsl::*;
    let contact = diesel::update(crm_contacts.filter(id.eq(contact_id)))
        .set(&data)
        .returning(CrmContact::as_returning())
        .get_result(&mut conn)
        .map_err(|e| e.to_string())?;
    signals::emit(ChangeEvent::EntityChanged("crm_contact".into(), contact.id));
    Ok(contact)
}

pub fn delete_crm_contact(db_path: &PathBuf, contact_id: i32) -> Result<(), String> {
    let mut conn = open_conn(db_path)?;
    use crate::db::schema::crm_contacts::dsl::*;
    diesel::delete(crm_contacts.filter(id.eq(contact_id)))
        .execute(&mut conn)
        .map_err(|e| e.to_string())?;
    signals::emit(ChangeEvent::EntityChanged("crm_contact".into(), contact_id));
    Ok(())
}

// ---------------------------------------------------------------------------
// Pipelines
// ---------------------------------------------------------------------------

pub fn get_crm_pipeline(db_path: &PathBuf, pipeline_id: i32) -> Result<CrmPipeline, String> {
    let mut conn = open_conn(db_path)?;
    use crate::db::schema::crm_pipelines::dsl::*;
    crm_pipelines
        .find(pipeline_id)
        .first::<CrmPipeline>(&mut conn)
        .map_err(|e| e.to_string())
}

pub fn get_crm_pipelines(db_path: &PathBuf) -> Result<Vec<CrmPipeline>, String> {
    let mut conn = open_conn(db_path)?;
    use crate::db::schema::crm_pipelines::dsl::*;
    crm_pipelines
        .order(name.asc())
        .load::<CrmPipeline>(&mut conn)
        .map_err(|e| e.to_string())
}

pub fn create_crm_pipeline(db_path: &PathBuf, data: NewCrmPipeline) -> Result<CrmPipeline, String> {
    let mut conn = open_conn(db_path)?;
    use crate::db::schema::crm_pipelines::dsl::*;
    let pipeline = diesel::insert_into(crm_pipelines)
        .values(&data)
        .returning(CrmPipeline::as_returning())
        .get_result(&mut conn)
        .map_err(|e| e.to_string())?;
    signals::emit(ChangeEvent::EntityChanged("crm_pipeline".into(), pipeline.id));
    Ok(pipeline)
}

// ---------------------------------------------------------------------------
// Stages
// ---------------------------------------------------------------------------

pub fn get_crm_stages(db_path: &PathBuf, for_pipeline: Option<i32>) -> Result<Vec<CrmStage>, String> {
    let mut conn = open_conn(db_path)?;
    use crate::db::schema::crm_stages::dsl::*;
    let mut query = crm_stages.order((pipeline_id.asc(), display_order.asc())).into_boxed();
    if let Some(pid) = for_pipeline {
        query = query.filter(pipeline_id.eq(pid));
    }
    query
        .load::<CrmStage>(&mut conn)
        .map_err(|e| e.to_string())
}

pub fn create_crm_stage(db_path: &PathBuf, data: NewCrmStage) -> Result<CrmStage, String> {
    let mut conn = open_conn(db_path)?;
    use crate::db::schema::crm_stages::dsl::*;
    let stage = diesel::insert_into(crm_stages)
        .values(&data)
        .returning(CrmStage::as_returning())
        .get_result(&mut conn)
        .map_err(|e| e.to_string())?;
    signals::emit(ChangeEvent::EntityChanged("crm_stage".into(), stage.id));
    Ok(stage)
}

// ---------------------------------------------------------------------------
// Deals
// ---------------------------------------------------------------------------

pub fn get_crm_deals(db_path: &PathBuf) -> Result<Vec<CrmDeal>, String> {
    let mut conn = open_conn(db_path)?;
    use crate::db::schema::crm_deals::dsl::*;
    crm_deals
        .order(created_at.desc())
        .load::<CrmDeal>(&mut conn)
        .map_err(|e| e.to_string())
}

pub fn create_crm_deal(db_path: &PathBuf, data: NewCrmDeal) -> Result<CrmDeal, String> {
    let mut conn = open_conn(db_path)?;
    use crate::db::schema::crm_deals::dsl::*;
    let deal = diesel::insert_into(crm_deals)
        .values(&data)
        .returning(CrmDeal::as_returning())
        .get_result(&mut conn)
        .map_err(|e| e.to_string())?;
    signals::emit(ChangeEvent::EntityChanged("crm_deal".into(), deal.id));
    Ok(deal)
}

pub fn update_crm_deal(db_path: &PathBuf, deal_id: i32, data: UpdateCrmDeal) -> Result<CrmDeal, String> {
    let mut conn = open_conn(db_path)?;
    use crate::db::schema::crm_deals::dsl::*;
    let deal = diesel::update(crm_deals.filter(id.eq(deal_id)))
        .set(&data)
        .returning(CrmDeal::as_returning())
        .get_result(&mut conn)
        .map_err(|e| e.to_string())?;
    signals::emit(ChangeEvent::EntityChanged("crm_deal".into(), deal.id));
    Ok(deal)
}

pub fn delete_crm_deal(db_path: &PathBuf, deal_id: i32) -> Result<(), String> {
    let mut conn = open_conn(db_path)?;
    use crate::db::schema::crm_deals::dsl::*;
    diesel::delete(crm_deals.filter(id.eq(deal_id)))
        .execute(&mut conn)
        .map_err(|e| e.to_string())?;
    signals::emit(ChangeEvent::EntityChanged("crm_deal".into(), deal_id));
    Ok(())
}

// ---------------------------------------------------------------------------
// Activities
// ---------------------------------------------------------------------------

pub fn get_crm_activities(db_path: &PathBuf) -> Result<Vec<CrmActivity>, String> {
    let mut conn = open_conn(db_path)?;
    use crate::db::schema::crm_activities::dsl::*;
    crm_activities
        .order(created_at.desc())
        .load::<CrmActivity>(&mut conn)
        .map_err(|e| e.to_string())
}

pub fn create_crm_activity(db_path: &PathBuf, data: NewCrmActivity) -> Result<CrmActivity, String> {
    let mut conn = open_conn(db_path)?;
    use crate::db::schema::crm_activities::dsl::*;
    let activity = diesel::insert_into(crm_activities)
        .values(&data)
        .returning(CrmActivity::as_returning())
        .get_result(&mut conn)
        .map_err(|e| e.to_string())?;
    signals::emit(ChangeEvent::EntityChanged("crm_activity".into(), activity.id));
    Ok(activity)
}

pub fn update_crm_activity(db_path: &PathBuf, activity_id: i32, data: UpdateCrmActivity) -> Result<CrmActivity, String> {
    let mut conn = open_conn(db_path)?;
    use crate::db::schema::crm_activities::dsl::*;
    let activity = diesel::update(crm_activities.filter(id.eq(activity_id)))
        .set(&data)
        .returning(CrmActivity::as_returning())
        .get_result(&mut conn)
        .map_err(|e| e.to_string())?;
    signals::emit(ChangeEvent::EntityChanged("crm_activity".into(), activity.id));
    Ok(activity)
}

// ---------------------------------------------------------------------------
// Notes
// ---------------------------------------------------------------------------

pub fn get_crm_notes(db_path: &PathBuf) -> Result<Vec<CrmNote>, String> {
    let mut conn = open_conn(db_path)?;
    use crate::db::schema::crm_notes::dsl::*;
    crm_notes
        .order(created_at.desc())
        .load::<CrmNote>(&mut conn)
        .map_err(|e| e.to_string())
}

pub fn create_crm_note(db_path: &PathBuf, data: NewCrmNote) -> Result<CrmNote, String> {
    let mut conn = open_conn(db_path)?;
    use crate::db::schema::crm_notes::dsl::*;
    let note = diesel::insert_into(crm_notes)
        .values(&data)
        .returning(CrmNote::as_returning())
        .get_result(&mut conn)
        .map_err(|e| e.to_string())?;
    signals::emit(ChangeEvent::EntityChanged("crm_note".into(), note.id));
    Ok(note)
}

pub fn delete_crm_note(db_path: &PathBuf, note_id: i32) -> Result<(), String> {
    let mut conn = open_conn(db_path)?;
    use crate::db::schema::crm_notes::dsl::*;
    diesel::delete(crm_notes.filter(id.eq(note_id)))
        .execute(&mut conn)
        .map_err(|e| e.to_string())?;
    signals::emit(ChangeEvent::EntityChanged("crm_note".into(), note_id));
    Ok(())
}

// ---------------------------------------------------------------------------
// Sync Queue
// ---------------------------------------------------------------------------

pub fn get_pending_sync_items(db_path: &PathBuf) -> Result<Vec<CrmSyncQueue>, String> {
    let mut conn = open_conn(db_path)?;
    use crate::db::schema::crm_sync_queue::dsl::*;
    crm_sync_queue
        .filter(is_processing.eq(false))
        .order((priority.asc(), created_at.asc()))
        .load::<CrmSyncQueue>(&mut conn)
        .map_err(|e| e.to_string())
}

pub fn add_to_sync_queue(db_path: &PathBuf, data: NewCrmSyncQueue) -> Result<CrmSyncQueue, String> {
    let mut conn = open_conn(db_path)?;
    use crate::db::schema::crm_sync_queue::dsl::*;
    diesel::insert_into(crm_sync_queue)
        .values(&data)
        .returning(CrmSyncQueue::as_returning())
        .get_result(&mut conn)
        .map_err(|e| e.to_string())
}
