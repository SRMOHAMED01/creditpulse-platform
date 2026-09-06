import client from "./client";

export const submitCreditApplication = (application) =>
  client.post("/credit/apply", application);
