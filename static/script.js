document.addEventListener(
    "DOMContentLoaded",
    function () {

        const analyzeButton =
            document.getElementById("analyzeButton");

        const resumeInput =
            document.getElementById("resume");

        const jobDescription =
            document.getElementById("jobDescription");

        const message =
            document.getElementById("message");

        const resultsSection =
            document.getElementById("resultsSection");


        analyzeButton.addEventListener(
            "click",
            async function () {

                const file =
                    resumeInput.files[0];


                if (!file) {

                    message.textContent =
                        "Please choose a resume first.";

                    return;
                }


                const formData =
                    new FormData();


                formData.append(
                    "resume",
                    file
                );


                formData.append(
                    "job_description",
                    jobDescription.value
                );


                message.textContent =
                    "🔍 Analyzing your resume...";


                analyzeButton.disabled = true;


                try {

                    const response =
                        await fetch(
                            "/analyze",
                            {
                                method: "POST",
                                body: formData
                            }
                        );


                    const data =
                        await response.json();


                    if (!response.ok) {

                        message.textContent =
                            data.error ||
                            "Analysis failed.";

                        return;
                    }


                    message.textContent =
                        "✅ Analysis completed!";


                    displayResults(data);


                }
                catch (error) {

                    message.textContent =
                        "❌ Could not connect to server.";

                    console.error(error);

                }
                finally {

                    analyzeButton.disabled = false;

                }

            }
        );


        function displayResults(data) {

            resultsSection.style.display =
                "block";


            document.getElementById("score")
                .textContent = data.score;


            document.getElementById(
                "matchPercentage"
            ).textContent =
                data.match_percentage + "%";


            displaySkills(
                "skillsContainer",
                data.skills
            );


            displaySkills(
                "missingSkillsContainer",
                data.missing_skills
            );


            displaySkills(
                "matchedSkillsContainer",
                data.matched_skills
            );


            const recommendations =
                document.getElementById(
                    "recommendationsContainer"
                );


            recommendations.innerHTML = "";


            data.recommendations.forEach(
                function (recommendation) {

                    const li =
                        document.createElement("li");

                    li.textContent =
                        recommendation;

                    recommendations.appendChild(li);

                }
            );


            resultsSection.scrollIntoView({
                behavior: "smooth"
            });

        }


        function displaySkills(
            containerId,
            skills
        ) {

            const container =
                document.getElementById(
                    containerId
                );


            container.innerHTML = "";


            if (skills.length === 0) {

                container.textContent =
                    "No skills found.";

                return;
            }


            skills.forEach(
                function (skill) {

                    const span =
                        document.createElement(
                            "span"
                        );


                    span.classList.add(
                        "skill-tag"
                    );


                    span.textContent =
                        skill;


                    container.appendChild(
                        span
                    );

                }
            );

        }

    }
);
