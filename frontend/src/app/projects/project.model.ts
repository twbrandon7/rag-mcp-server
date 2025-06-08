export interface ProjectModel {
  project_id: string;
  user_id: string;
  project_name: string;
  created_at: string;
}

export interface ProjectCreate {
  project_name: string;
}

export interface ProjectUpdate {
  project_name: string;
}

export interface ProjectResponse {
  project_id: string;
  user_id: string;
  project_name: string;
  created_at: string;
}
