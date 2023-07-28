new Vue({
    el: '#app',
    data: {
        video_link: '',
        chunk_size: '',
        language: '',
        prompt: '',
        end_prompt: '',
        prompts: [],
        final_text: ''
    },
    methods: {
        onSubmit() {
            axios.post('/', {
                video_link: this.video_link,
                chunk_size: this.chunk_size,
                language: this.language,
                prompt: this.prompt,
                end_prompt: this.end_prompt
            })
            .then(response => {
                this.prompts = response.data.prompts;
                this.final_text = response.data.final_text;
            })
            .catch(error => {
                console.log(error);
            });
        }
    }
});
