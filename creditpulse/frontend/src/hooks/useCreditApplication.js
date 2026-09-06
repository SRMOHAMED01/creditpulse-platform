import { useMutation } from "@tanstack/react-query";
import { submitCreditApplication } from "../api/credit";

export default function useCreditApplication() {
	return useMutation({
		mutationFn: async (application) => {
			const { data } = await submitCreditApplication(application);
			return data;
		},
	});
}
