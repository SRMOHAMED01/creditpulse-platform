import client from "./client";

export const submitCreditApplication = (application) =>
  client.post("/credit/apply", application);

export const getCreditApplications = (params = {}) =>
  client.get("/credit/applications", { params });

export const getCreditApplication = (id) =>
  client.get(`/credit/applications/${id}`);
